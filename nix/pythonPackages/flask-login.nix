{
  buildPythonPackage,
  fetchPypi,
  flask,
  werkzeug,
}:
let
  pypiSource = (builtins.fromJSON (builtins.readFile ./flask-login.json));
in
buildPythonPackage rec {
  pname = pypiSource.pname;
  version = pypiSource.version;
  format = "setuptools";
  src = fetchPypi pypiSource;
  propagatedBuildInputs = [
    flask
    werkzeug
  ];
  doCheck = false;
}
