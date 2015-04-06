all: debug

debug:
	python run.py

test:
	py.test -s test.py

.PHONY: clean
clean:
	-@rm app/app.db
	-@find . -name '*.pyc' -exec rm {} \;
