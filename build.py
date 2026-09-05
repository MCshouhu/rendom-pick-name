import PyInstaller.__main__
import os

# 打包参数
args = [
    '1.py',
    '--onefile',          # 单个文件
    '--windowed',         # 无控制台
    '--name=随机点名器',   # 程序名称
    '--clean',            # 清理缓存
    '--noconfirm',        # 不确认覆盖
    '--optimize=2',       # 优化级别
]

# 执行打包
PyInstaller.__main__.run(args)

print("打包完成！")
print(f"可执行文件位置: {os.path.abspath('dist/2702图形化点名.exe')}")
