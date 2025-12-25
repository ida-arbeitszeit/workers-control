{
  buildPythonPackage,
  fetchPypi,
  flask,
  babel,
  pytz,
  jinja2,
  poetry-core,
}:
let
  pypiSource = (builtins.fromJSON (builtins.readFile ./flask-babel.json));
in
buildPythonPackage rec {
  pname = pypiSource.pname;
  version = pypiSource.version;
  pyproject = true;
  src = fetchPypi pypiSource;
  build-system = [ poetry-core ];
  dependencies = [
    babel
    flask
    jinja2
    pytz
  ];
  doCheck = false;
}
