import os
import re
import urllib.request

def download_and_clean(secret_env_name, site_name):
    url = os.getenv(secret_env_name)
    if not url:
        print(f"提示: {secret_env_name} 未设置，跳过。")
        return False

    print(f"正在下载并清洗 {site_name} 原始数据...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            raw_content = response.read().decode('utf-8')
        
        # 修复挤在同一行的问题
        formatted_content = re.sub(r'(?<!\n)(DOMAIN(-SUFFIX|-KEYWORD)?|SRC-IP-CIDR|IP-CIDR6?)', r'\n\1', raw_content)
        lines = formatted_content.splitlines()
        
        clean_domains = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 【核心转换】：将 Mihomo 格式转换为 v2ray-rules-dat 工具认的格式
            # 例如将 "DOMAIN-SUFFIX,google.com" 转换为 "google.com"
            # 将 "DOMAIN,api.com" 转换为 "full:api.com"
            if "DOMAIN-SUFFIX," in line:
                domain = line.replace("DOMAIN-SUFFIX,", "").strip()
                clean_domains.append(domain)
            elif "DOMAIN," in line:
                domain = line.replace("DOMAIN,", "").strip()
                clean_domains.append(f"full:{domain}")
            elif "DOMAIN-KEYWORD," in line:
                domain = line.replace("DOMAIN-KEYWORD,", "").strip()
                clean_domains.append(f"keyword:{domain}")
            else:
                # 如果已经是纯域名
                clean_domains.append(line)

        # 去重
        clean_domains = list(dict.fromkeys(clean_domains))

        # 写入到工具指定的目录：geosite/<文件名>
        os.makedirs("geosite", exist_ok=True)
        with open(f"geosite/{site_name}", "w", encoding="utf-8") as f:
            f.write("\n".join(clean_domains) + "\n")
            
        print(f"成功预处理 {site_name}，共 {len(clean_domains)} 条规则。")
        return True
    except Exception as e:
        print(f"处理 {site_name} 失败: {e}")
        return False

if __name__ == "__main__":
    # 我们把生成的组分别命名为 mylocal 和 myproxy
    download_and_clean("LOCAL_LIST_URL", "mylocal")
    download_and_clean("PROXY_LIST_URL", "myproxy")
