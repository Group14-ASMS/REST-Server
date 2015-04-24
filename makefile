all: debug

debug:
	python run.py

rebuild-test:
	python rebuild-test.py

test:
	py.test -vv test.py

.PHONY: clean
clean:
	-@rm app/app.db
	-@rm -rf __pycache__
	-@find . -name '*.pyc' -exec rm {} \;
