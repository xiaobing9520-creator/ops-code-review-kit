#!/bin/bash
# =============================================================================
# 运维代码审核 - 补充扫描工具脚本
# 用途：自动检测已安装的扫描工具并运行，输出报告到 tool-reports/ 目录
# 使用方法：在待审核项目的根目录下运行 bash run-tool-scans.sh
# =============================================================================

set -euo pipefail

REPORT_DIR="tool-reports"
mkdir -p "$REPORT_DIR"

echo "========================================"
echo "  运维代码审核 - 补充扫描工具"
echo "========================================"
echo ""
echo "报告输出目录: $REPORT_DIR/"
echo ""

TOOLS_RUN=0
TOOLS_SKIPPED=0

# -----------------------------------------------------------------------------
# Trivy - 依赖漏洞扫描 (SCA)
# -----------------------------------------------------------------------------
if command -v trivy &> /dev/null; then
    echo "[*] 检测到 Trivy，开始依赖漏洞扫描..."
    trivy fs \
        --format json \
        --output "$REPORT_DIR/trivy-sca.json" \
        --scanners vuln \
        . 2>/dev/null || true
    echo "    报告已保存: $REPORT_DIR/trivy-sca.json"
    TOOLS_RUN=$((TOOLS_RUN + 1))
else
    echo "[ ] Trivy 未安装，跳过依赖漏洞扫描"
    echo "    安装方法: brew install trivy 或参考 https://trivy.dev"
    TOOLS_SKIPPED=$((TOOLS_SKIPPED + 1))
fi

echo ""

# -----------------------------------------------------------------------------
# Semgrep - 代码安全扫描 (SAST)
# -----------------------------------------------------------------------------
if command -v semgrep &> /dev/null; then
    echo "[*] 检测到 Semgrep，开始代码安全扫描..."
    semgrep scan \
        --config auto \
        --json \
        --output "$REPORT_DIR/semgrep.json" \
        . 2>/dev/null || true
    echo "    报告已保存: $REPORT_DIR/semgrep.json"
    TOOLS_RUN=$((TOOLS_RUN + 1))
else
    echo "[ ] Semgrep 未安装，跳过代码安全扫描"
    echo "    安装方法: pip install semgrep 或参考 https://semgrep.dev"
    TOOLS_SKIPPED=$((TOOLS_SKIPPED + 1))
fi

echo ""

# -----------------------------------------------------------------------------
# Checkov - IaC 配置扫描
# -----------------------------------------------------------------------------
if command -v checkov &> /dev/null; then
    echo "[*] 检测到 Checkov，开始 IaC 配置扫描..."
    checkov \
        -d . \
        --output json \
        --output-file-path "$REPORT_DIR" \
        --quiet 2>/dev/null || true
    # Checkov outputs to results_json.json in the specified directory
    if [ -f "$REPORT_DIR/results_json.json" ]; then
        mv "$REPORT_DIR/results_json.json" "$REPORT_DIR/checkov.json"
    fi
    echo "    报告已保存: $REPORT_DIR/checkov.json"
    TOOLS_RUN=$((TOOLS_RUN + 1))
else
    echo "[ ] Checkov 未安装，跳过 IaC 配置扫描"
    echo "    安装方法: pip install checkov 或参考 https://checkov.io"
    TOOLS_SKIPPED=$((TOOLS_SKIPPED + 1))
fi

echo ""

# -----------------------------------------------------------------------------
# 扫描完成汇总
# -----------------------------------------------------------------------------
echo "========================================"
echo "  扫描完成"
echo "========================================"
echo "  已运行工具: $TOOLS_RUN"
echo "  已跳过工具: $TOOLS_SKIPPED"
echo ""

if [ "$TOOLS_RUN" -gt 0 ]; then
    echo "报告文件:"
    ls -la "$REPORT_DIR/"
    echo ""
    echo "这些报告将在 Kiro 审核时被自动读取。"
else
    echo "未运行任何扫描工具。Kiro 仍可独立完成审核，"
    echo "但建议安装至少一个扫描工具以获得更完整的审核数据。"
fi
