all: debug

debug:
	python run.py

.PHONY: clean
clean:
	-@rm app.db
	-@find . -name '*.pyc' -exec rm {} \;
