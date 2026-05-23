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
        
        # 修复可能挤在同一行的问题
        formatted_content = re.sub(r'(?<!\n)(DOMAIN(-SUFFIX|-KEYWORD)?|SRC-IP-CIDR|IP-CIDR6?)', r'\n\1', raw_content)
        lines = formatted_content.splitlines()
        
        clean_domains = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 🌟 关键修正：如果规则中包含 IP-CIDR / SRC-IP-CIDR 等 IP 判定，或者是纯纯的 IP 段，直接跳过
            # 理由：GeoSite 二进制文件只能收录域名类规则
            if any(ip_keyword in line.upper() for ip_keyword in ["IP-CIDR", "IP-CIDR6", "SRC-IP-CIDR"]):
                print(f"[{site_name}] 过滤掉不属于域名的 IP 规则: {line}")
                continue
                
            # 使用正则简单过滤可能直接写出来的纯 IP 地址或 CIDR（比如 172.18.0.0/16）
            if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', line):
                print(f"[{site_name}] 过滤掉裸 IP/CIDR 规则: {line}")
                continue

            # 【转换为 GeoSite 编译器认的格式】
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
                # 已经是标准域名形式
                clean_domains.append(line)

        # 去重
        clean_domains = list(dict.fromkeys(clean_domains))

        # 写入到目录
        os.makedirs("geosite", exist_ok=True)
        with open(f"geosite/{site_name}", "w", encoding="utf-8") as f:
            f.write("\n".join(clean_domains) + "\n")
            
        print(f"成功预处理 {site_name}，共 {len(clean_domains)} 条有效域名规则。")
        return True
    except Exception as e:
        print(f"处理 {site_name} 失败: {e}")
        return False

if __name__ == "__main__":
    download_and_clean("LOCAL_LIST_URL", "mylocal")
    download_and_clean("PROXY_LIST_URL", "myproxy")
