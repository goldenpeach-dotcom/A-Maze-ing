# 課題文Chapter III.5ターゲット(lint-strictは任意)

.PHONY: install run debug clean lint lint-strict

PYTHON := python3
CONFIG := config.txt

# 依存関係のインストール(pip/uv/pipxのどれでも可)
install:
	$(PYTHON) -m pip install -r requirements.txt

# メインスクリプトの実行
run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

# pdbを使ったデバッグ実行
debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

# 一時ファイル・キャッシュの削除
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

# 課題指定flake8/mypyオプション(必須/mandatory)
lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

# 厳しめチェック(課題推奨)
lint-strict:
	flake8 .
	mypy . --strict
