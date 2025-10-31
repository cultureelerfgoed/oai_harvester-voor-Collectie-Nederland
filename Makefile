.PHONY: help run lint clean

help:
	@echo "make run            # Interactief starten"
	@echo "make lint           # Syntaxischeck"
	@echo "make clean          # Verwijdert logs, state en dumps"

run:
	python oai_harvester.py

lint:
	python -m py_compile oai_harvester.py

clean:
	rm -f *.log *.state.json last_response_dump.xml *.csv *.jsonl
