.PHONY: run
run:
	docker run -v "$(shell pwd):/workspace/search_engineering" \
		-v ""$(shell pwd)/datasets:/workspace/datasets" \
		--network opensearch-net --name search_engineering \
		-it gsingers/search_engineering:latest