# RopeDP Makefile

.PHONY: help install install-dev test clean lint format docs

help:  ## 显示帮助信息
	@echo "RopeDP - 代码仓数据处理工具"
	@echo ""
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## 安装依赖
	pip install -r requirements.txt

install-dev:  ## 安装开发依赖
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy

test:  ## 运行测试
	python -m pytest tests/ -v --cov=src/repodp --cov-report=html

test-basic:  ## 运行基本测试
	python tests/test_basic.py

clean:  ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf data/

lint:  ## 代码检查
	flake8 src/ tests/
	mypy src/repodp/

format:  ## 代码格式化
	black src/ tests/

docs:  ## 生成文档
	@echo "文档生成功能待实现"

run-example:  ## 运行示例
	python examples/example_usage.py

run-jsonl-example:  ## 运行JSONL示例
	python examples/jsonl_example.py

setup:  ## 初始化项目
	mkdir -p data/{repos,reports,backups,extracted,logs}
	cp config/config.yaml data/
	@echo "项目初始化完成"

check:  ## 检查项目状态
	@echo "检查项目状态..."
	@echo "Python版本:"
	@python --version
	@echo ""
	@echo "已安装的包:"
	@pip list | grep -E "(click|gitpython|pandas|numpy|tqdm|pyyaml|matplotlib|seaborn|plotly|jupyter)"
	@echo ""
	@echo "项目结构:"
	@find . -type f -name "*.py" | head -10

