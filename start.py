import os
import sys
import subprocess


def check_dependencies():
    """检查并安装必要的依赖库"""
    required_packages = ['chromadb', 'openai', 'pdfplumber', 'python-docx']
    missing_packages = []

    print("🔍 正在检查环境依赖...")
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"⚠️ 发现缺失库: {missing_packages}")
        print("🚀 正在自动安装缺失的库 (可能需要几分钟)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("✅ 依赖安装完成！")
    else:
        print("✅ 所有依赖已就绪。")


def run_script(script_name, description):
    """运行指定的 Python 脚本"""
    if not os.path.exists(script_name):
        print(f"❌ 错误: 找不到文件 {script_name}，请确保它在当前目录下。")
        return

    print(f"\n{'=' * 40}")
    print(f"🚀 正在启动: {description}")
    print(f"{'=' * 40}\n")

    # 使用 subprocess 运行脚本，保持输出可见
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行出错: {e}")
    except KeyboardInterrupt:
        print("\n👋 程序已手动停止。")


def main():
    print("欢迎使用 RAG 本地知识库问答系统启动器")

    # 1. 检查环境
    check_dependencies()

    # 2. 检查 API Key (简单检查，防止直接运行报错)
    # 注意：这里假设 auth.py 或环境变量中处理了 key，这里仅做提示
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("⚠️ 提示: 未检测到环境变量 DASHSCOPE_API_KEY。")
        print("   请确保已在 auth.py 或系统环境变量中配置了阿里云 DashScope API Key。\n")

    # 3. 提供菜单选择
    while True:
        print("\n请选择操作模式:")
        print("1. 📥 仅入库数据 (运行 script1.py)")
        print("2. 💬 启动问答系统 (运行 ASK.py)")
        print("3. 🔄 全量更新并启动 (先入库再问答)")
        print("0. 🚪 退出")

        choice = input("\n请输入选项 (0-3): ").strip()

        if choice == '1':
            run_script('script1.py', '数据入库流程')
        elif choice == '2':
            run_script('ASK.py', '智能问答系统')
        elif choice == '3':
            print("⏳ 正在执行全量更新...")
            run_script('script1.py', '数据入库流程')
            input("\n按回车键继续启动问答系统...")
            run_script('ASK.py', '智能问答系统')
        elif choice == '0':
            print("再见！")
            break
        else:
            print("无效输入，请重试。")


if __name__ == "__main__":
    main()