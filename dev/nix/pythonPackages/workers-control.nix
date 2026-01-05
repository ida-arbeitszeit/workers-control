{
  buildPythonPackage,
  postgresql,

  # python packages
  alembic,
  babel,
  psycopg2,
  email-validator,
  flask,
  flask-babel,
  flask-mail,
  flask-profiler,
  flask-talisman,
  flask-login,
  flask-wtf,
  matplotlib,
  parameterized,
  pytest,
  setuptools,
  sphinx,
  sphinx-rtd-theme,
}:
buildPythonPackage {
  pname = "workers-control";
  version = "0.1.4";
  src = ../../..;
  outputs = [
    "out"
    "doc"
  ];
  postPhases = [ "buildDocsPhase" ];
  pyproject = true;
  nativeCheckInputs = [
    pytest
    postgresql
    psycopg2
    parameterized
  ];
  buildInputs = [
    sphinx
    sphinx-rtd-theme
    babel
    setuptools
  ];
  dependencies = [
    alembic
    email-validator
    flask
    flask-babel
    flask-mail
    flask-talisman
    flask-login
    flask-wtf
    matplotlib
  ];
  buildDocsPhase = ''
    mkdir -p $doc/share/doc/workers-control
    python -m sphinx -a $src/docs $doc/share/doc/workers-control
  '';
  passthru.optional-dependencies = {
    profiling = [ flask-profiler ];
  };
  checkPhase = ''
    runHook preCheck

    # Run tests with SQLite.

    WOCO_TEST_DB=sqlite:////tmp/workers_control_test.db pytest -x

    # Run tests with PostgreSQL.

    POSTGRES_DIR=$(mktemp -d)
    initdb -D $POSTGRES_DIR
    postgres -h "" -k $POSTGRES_DIR -D $POSTGRES_DIR &
    POSTGRES_PID=$!
    until createdb -h $POSTGRES_DIR; do echo "Retry createdb"; done

    WOCO_TEST_DB="postgresql:///?host=$POSTGRES_DIR" pytest -x

    kill $POSTGRES_PID

    runHook postCheck
  '';
}
