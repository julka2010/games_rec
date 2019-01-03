# ====================== CONSTANTS SECTION ========================= #
#
compose_spec = "docker/docker-compose.yml"
dotenv = "./.env"
venv-name = "env"
#
# ==================== END CONSTANTS SECTION ======================= #


# ====================================================================
# Create/upgrade python3 virtual environment.
# ====================================================================
venv-init:
	python3 -m venv $(venv-name)
	# Subshell required here: you don't have sh env in make runtime
	(\
		source $(venv-name)/bin/activate && \
		pip install --upgrade pip && \
		pip install -r misc/requirements.txt \
	)

# ====================================================================
# Run database initialization process.
# ====================================================================
init-db:
	(\
		source $(dotenv) && \
		docker-compose -f $(compose_spec) exec \
			-e GAMES_REC_DB_NAME=$${GAMES_REC_DB_NAME} \
			-e GAMES_REC_DB_USER=$${GAMES_REC_DB_USER} \
			-e GAMES_REC_DB_PASS=$${GAMES_REC_DB_PASS} \
	 		psql sh -x /init-db.sh \
	)

# ====================================================================
# Run arbitrary docker-compose commands.
# ====================================================================
docker-compose:
	docker-compose -f $(compose_spec) --project-directory $(pwd) $(ARGS)


# ====================================================================
# Create docker-compose images from dockerfiles and spec provided in
# this Makefile.
# ====================================================================
dc-build: ARGS=build
dc-build: docker-compose

# ====================================================================
# Run docker-compose using env and spec provided in this Makefile
# ====================================================================
up:
	(\
		source $(dotenv) && \
	 	docker-compose -f $(compose_spec) --project-directory $(CURDIR) up \
	)

# ====================================================================
# Bring docker-compose down (for cases when you use -d flag)
# ====================================================================
down: ARGS=down
down: docker-compose

# ====================================================================
# Install UI dependencies
# ====================================================================
ui-dep:
	(\
		cd ui && \
		npm i \
	)

# ====================================================================
# Build UI bundle
# ====================================================================
ui-build:
	(\
		cd ui && \
		npm run-script build \
	)

# ====================================================================
# Copy templates in $PROJECT_ROOT/env_vars (no override)
# ====================================================================
env-init:
	(\
		sh ./misc/scripts/init.sh \
	)
# ====================================================================
# Copy templates in $PROJECT_ROOT/env_vars (with override)
# ====================================================================
env-override:
	(\
		sh ./misc/scripts/init.sh --override \
	)

# ====================================================================
# Compose .env file from sources declared in $PROJECT_ROOT/env_vars
# ====================================================================
env-compose:
	(\
		sh ./misc/scripts/compose.sh \
	)

