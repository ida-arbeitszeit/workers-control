{
  buildPythonPackage,
  postgresql,

  # python packages
  alembic,
  babel,
  click,
  psycopg2,
  email-validator,
  flask,
  flask-wtf,
  itsdangerous,
  jinja2,
  markupsafe,
  matplotlib,
  parameterized,
  pytest,
  setuptools,
  sphinx,
  sphinx-rtd-theme,
  sqlalchemy,
  werkzeug,
  wtforms,
}:
let
  pyproject = builtins.fromTOML (builtins.readFile ../../../pyproject.toml);
in
buildPythonPackage {
  pname = "workers-control";
  version = pyproject.project.version;
  src = ../../..;
  outputs = [
    "out"
    "doc"
  ];
  postPhases = [ "buildDocsPhase" ];
  pyproject = true;
  nativeCheckInputs = [
    alembic
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
    click
    email-validator
    flask
    flask-wtf
    itsdangerous
    jinja2
    markupsafe
    matplotlib
    sqlalchemy
    werkzeug
    wtforms
  ];
  buildDocsPhase = ''
    mkdir -p $doc/share/doc/workers-control
    python -m sphinx -a $src/docs $doc/share/doc/workers-control
  '';
  checkPhase = ''
    runHook preCheck

    # Run tests with SQLite.

    SQLITE_DIR=$(mktemp -d)
    WOCO_TEST_DB=sqlite:///$SQLITE_DIR/workers_control_test.db pytest -x

    # Run tests with PostgreSQL.

    POSTGRES_DIR=$(mktemp -d)
    initdb -D $POSTGRES_DIR
    postgres -h "" -k $POSTGRES_DIR -D $POSTGRES_DIR &
    POSTGRES_PID=$!
    trap "kill $POSTGRES_PID" EXIT
    until createdb -h $POSTGRES_DIR; do echo "Retry createdb"; done

    WOCO_TEST_DB="postgresql:///?host=$POSTGRES_DIR" pytest -x

    runHook postCheck
  '';
}
