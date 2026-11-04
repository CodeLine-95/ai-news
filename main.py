"""平台发布入口。

发布脚本（publish.js / lib.js 的 buildRuntimePlan）对 Python 项目的默认
启动命令是 `python main.py`。本项目实际入口是 server.py，若不提供 main.py，
平台自启动会执行 `python main.py` 必然失败，表现为：

    {"code": 504, "msg": "service on port 8080 not ready after 30000ms"}

即平台侧 30 秒就绪探测超时——服务进程根本没起来，而不是启动太慢。

本文件只做一件事：复用 server.py 里已经构建好的 FastAPI app 并启动它。
真正的启动逻辑（含 uvicorn.run、后台调度器、翻译引擎预热）全部留在
server.py 的 __main__ 分支里，避免两处重复。

注意：server.py 在被 import 时不会自动启动服务（启动逻辑在
`if __name__ == "__main__":` 内），因此这里 import 是安全的。
"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

import server  # noqa: E402  必须在 sys.path 设置之后导入


def main():
    port = int(os.environ.get("PORT", "8080"))
    # 走 server.py 的标准启动路径：预热翻译引擎 + 启动后台调度器 + 监听端口。
    # 这里不重复实现，只把 uvicorn 拉起来，保证与本地运行行为完全一致。
    import uvicorn

    # 日志落盘必须在 uvicorn 启动前完成：平台拉起进程时 stdout 未必指向
    # 日志文件，靠 shell 重定向的方案在进程重启后会丢，导致无法巡检。
    server.setup_file_logging()

    server.load_data()

    # 启动即用人工定稿回填存量译文（部署端 data/ 是持久卷，可能与本地脱节）。
    try:
        server.apply_manual_overrides_on_startup()
    except Exception as e:  # noqa
        print("[main] 启动回填人工定稿异常:", e, flush=True)

    def _warmup():
        try:
            server.translate.translate_list(["warmup"])
            print("[main] 翻译引擎预热完成", flush=True)
        except Exception as e:  # noqa
            print("[main] 翻译引擎预热失败:", e, flush=True)

    import threading

    threading.Thread(target=_warmup, daemon=True).start()
    threading.Thread(target=server.scheduler_loop, daemon=True).start()
    uvicorn.run(server.app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
