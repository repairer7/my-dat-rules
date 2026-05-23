name: Build Separate Binary Dats

on:
  schedule:
    - cron: '0 22 * * *'
  workflow_dispatch:

jobs:
  build-dats:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: 1. 检出仓库
        uses: actions/checkout@v4

      - name: 2. 初始化 Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: 3. 初始化 Go 语言环境
        uses: actions/setup-go@v5
        with:
          go-version: '>=1.20'

      - name: 4. 解析 Gist 并转换为编译输入格式
        env:
          LOCAL_LIST_URL: ${{ secrets.LOCAL_LIST_URL }}
          PROXY_LIST_URL: ${{ secrets.PROXY_LIST_URL }}
        run: python generate.py

      - name: 5. 分别编译并压制 local.dat 和 proxy.dat
        run: |
          # 克隆官方工具源码
          git clone --depth=1 https://github.com/v2fly/domain-list-community.git compiler
          cd compiler
          
          # 🌟 第一次编译：压制生成独立的二进制 local.dat
          if [ -d "../temp_local/data" ]; then
            go run main.go --datapath=../temp_local/data --outputdir=../ --outputname=local.dat
          fi
          
          # 🌟 第二次编译：压制生成独立的二进制 proxy.dat
          if [ -d "../temp_proxy/data" ]; then
            go run main.go --datapath=../temp_proxy/data --outputdir=../ --outputname=proxy.dat
          fi

      - name: 6. 清理残留并推送到仓库
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          
          # 移除所有临时文本和编译器缓存
          rm -rf temp_local temp_proxy compiler
          
          # 将生成的两份完全加密、二进制的 .dat 文件提交进仓库
          git add local.dat proxy.dat
          
          if ! git diff --staged --quiet; then
            git commit -m "chore: 自动压制独立二进制 Dat 文件 $(date +'%Y-%m-%d %H:%M:%S') [skip ci]"
            git push origin main
            echo ">> 独立的 local.dat 和 proxy.dat 二进制文件已成功部署。"
          else
            echo ">> 内容无任何变化，跳过本次推送。"
          fi
