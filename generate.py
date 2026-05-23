import os
import re
import urllib.request

def clean_and_save(secret_env_name, output_filename):
    # 从环境变量中读取隐藏的 URL
    url = os.getenv(secret_env_name)
    
    if not url:
        print(f"提示: 环境变量 {secret_env_name} 未设置或为空，跳过此文件。")
        return

    print(f"正在从 {secret_env_name} 获取原始数据...")
    
    try:
        # 添加 请求头 防止被 GitHub 拦截
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as response:
            raw_content = response.read().decode('utf-8')
        
        # 【核心清洗逻辑】
        # 1. 如果原始数据挤在了一行（如 DOMAIN-SUFFIX,a.comDOMAIN-SUFFIX,b.com）
        # 使用正则在 DOMAIN-SUFFIX 或 DOMAIN 前面强制加上换行符
        formatted_content = re.sub(r'(?<!\n)(DOMAIN(-SUFFIX|-KEYWORD)?|SRC-IP-CIDR|IP-CIDR6?)', r'\n\1', raw_content)
        
        # 2. 按行分割并去除每行前后的空格、回车
        lines = [line.strip() for line in formatted_content.splitlines()]
        
        # 3. 去重且保持原有顺序，同时过滤掉空行
        seen = set()
        clean_lines = []
        for line in lines:
            if line and line not in seen:
                seen.add(line)
                clean_lines.append(line)
        
        # 4. 写入文件
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(clean_lines) + '\n')
            
        print(f"成功生成并清洗文件: {output_filename} (共 {len(clean_lines)} 条规则)")
    except Exception as e:
        print(f"处理 {output_filename} 时发生异常: {e}")

if __name__ == "__main__":
    # 分别处理直连列表和代理列表
    clean_and_save("LOCAL_LIST_URL", "local.dat")
    clean_and_save("PROXY_LIST_URL", "proxy.dat")
