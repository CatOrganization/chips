

build:
	@docker build -t chips .

run:
	@docker rm -f chips || echo 'no container'
	@docker run \
		-v /Users/rickybarillas/OneDrive-GeorgiaInstituteofTechnology/coding/chips/chips:/workdir/chips \
		--name chips \
		chips