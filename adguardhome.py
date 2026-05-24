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
    
    # 🌟 核心改进：严格匹配标准域名的正则表达式（如 abc.com, sub.abc.com.cn）
    # 域名只能由字母、数字、减号 . 组成，且最后必须是 2-12 位的顶级域后缀
    strict_domain_re = re.compile(r'^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?$')

    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
            
        # 核心需求：去除含有 quark (夸克) 关键词的规则
        if "quark" in line.lower():
            continue
            
        extracted_domain = None

        # A. 提取 ||example.com^ 语法
        if line.startswith("||") and "^" in line:
            parts = line.split("^")
            potential_domain = parts[0].replace("||", "").strip()
            # 排除带有特殊修饰符、通配符 * 或修饰路径的行
            if not any(char in potential_domain for char in ["*", "/", "?", ":", "@", "_"]):
                extracted_domain = potential_domain

        # B. 提取类似于 hosts 封杀的明文裸域名
        elif not line.startswith("!") and not line.startswith("["):
            # 如果这一行本身就没有特殊字符，尝试直接验证是否为纯域名
            if not any(char in line for char in ["*", "/", "?", ":", "@", "_", "||", "^", "##", "@@"]):
                extracted_domain = line

        # 🌟 终极防崩校验：通过上面的提取后，必须再走一次严格的纯域名格式过滤
        if extracted_domain:
            extracted_domain = extracted_domain.lower().strip()
            
            # 1. 确保符合标准的域名正则
            if strict_domain_re.match(extracted_domain):
                # 2. 排除纯 IP / CIDR 地址
                if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', extracted_domain):
                    continue
                # 3. 排除一些常见的公共无效前缀
                if extracted_domain in ["localhost", "127.0.0.1", "0.0.0.0"]:
                    continue
                    
                clean_domains.append(extracted_domain)

    # 3. 彻底去重
    clean_domains = list(dict.fromkeys(clean_domains))
    print(f"广告规则提取完成：严格过滤后，共获得 {len(clean_domains)} 条纯正广告域名。")

    # 4. 写入编译器的临时目录
    temp_dir = "temp_adguardhome/data"
    os.makedirs(temp_dir, exist_ok=True)
    with open(f"{temp_dir}/target", "w", encoding="utf-8") as f:
        f.write("\n".join(clean_domains) + "\n")
    print("已成功为编译器准备好严格清洗后的 adguardhome 临时输入源。")

if __name__ == "__main__":
    fetch_and_extract_domains()
