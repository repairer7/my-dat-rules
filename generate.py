import os
import urllib.request

def download_and_save(secret_env_name, output_filename):
    # 从环境变量中读取隐藏的 URL
    url = os.getenv(secret_env_name)
    
    if not url:
        print(f"错误: 环境变量 {secret_env_name} 未设置。")
        return

    print(f"正在从 {secret_env_name} 获取数据...")
    
    try:
        # 添加 User-Agent 防止被拦截
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
        
        # 将内容写入对应的 .dat 文件
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"成功生成 {output_filename}！")
    except Exception as e:
        print(f"获取或生成 {output_filename} 时发生错误: {e}")

if __name__ == "__main__":
    # 分别调用两个列表
    download_and_save("LOCAL_LIST_URL", "local.dat")
    download_and_save("PROXY_LIST_URL", "proxy.dat")
