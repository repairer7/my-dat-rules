import os
import re
import urllib.request

def fetch_and_extract_domains():
    urls = [
        "https://fastly.jsdelivr.net/gh/xinggsf/Adblock-Plus-Rule@master/rule.txt",
        "https://fastly.jsdelivr.net/gh/xinggsf/Adblock-Plus-Rule@master/mv.txt",
        "https://easylist-downloads.adblockplus.org/easylistchina.txt"
    ]
    
    raw_lines = []
    
    # 1. 批量下载多份规则
    for url in urls:
        print(f"正在下载广告规则: {url}")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')
                raw_lines.extend(content.splitlines())
        except Exception as e:
            print(f"下载失败 (跳过): {url}, 错误原因: {e}")

    clean_domains = []
    
    # 2. ABP 语法转 GeoSite 域名解析逻辑
    # 匹配 ||example.com^ 或 ||sub.example.com^ 等标准屏蔽域名语法
    domain_pattern = re.compile(r'^\|\|([a-zA-Z0-9\-\_\.]+)\^')

    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
            
        # 🌟 核心需求：去除含有 quark (夸克) 关键词的规则
        if "quark" in line.lower():
            continue
            
        # 提取域名成分
        match = domain_pattern.match(line)
        if match:
            domain = match.group(1)
            
            # 排除含有通配符 * 或者纯 IP 的不合格域名
            if "*" in domain or re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', domain):
                continue
                
            # 转换为 GeoSite 格式 (默认当做域名后缀处理，最符合广告拦截逻辑)
            clean_domains.append(domain)
        else:
            # 尝试兜底匹配直接写出来的裸域名（常用于 hosts 形式的广告源）
            if re.match(r'^[a-zA-Z0-9\-\_\.]+\.[a-zA-Z]{2,12}$', line):
                if not any(k in line.lower() for k in ["localhost", "127.0.0.1"]):
                    clean_domains.append(line)

    # 3. 彻底去重并保持排序
    clean_domains = list(dict.fromkeys(clean_domains))
    print(f"广告规则提取完成：去重及过滤 quark 后，共获得 {len(clean_domains)} 条有效广告域名。")

    # 4. 写入编译器的临时目录，内部标签统一叫 "target"
    temp_dir = "temp_adguardhome/data"
    os.makedirs(temp_dir, exist_ok=True)
    with open(f"{temp_dir}/target", "w", encoding="utf-8") as f:
        f.write("\n".join(clean_domains) + "\n")
    print("已成功为编译器准备好 adguardhome 临时输入源。")

if __name__ == "__main__":
    fetch_and_extract_domains()
