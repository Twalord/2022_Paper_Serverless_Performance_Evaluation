all: magick no-processing dummy dummy-sleep

openfaas_domain = YOUR URL HERE

magick:
	sudo faas build -f magick-example.yml
	sudo faas push -f magick-example.yml
	faas deploy -f magick-example.yml --gateway $(openfaas_domain)

no-processing:
	sudo faas build -f magick-example-no-processing.yml
	sudo faas push -f magick-example-no-processing.yml
	faas deploy -f magick-example-no-processing.yml --gateway $(openfaas_domain)

dummy:
	sudo faas build -f magick-example-dummy.yml
	sudo faas push -f magick-example-dummy.yml
	faas deploy -f magick-example-dummy.yml --gateway $(openfaas_domain)

dummy-sleep:
	sudo faas build -f magick-example-dummy-sleep.yml
	sudo faas push -f magick-example-dummy-sleep.yml
	faas deploy -f magick-example-dummy-sleep.yml --gateway $(openfaas_domain)

