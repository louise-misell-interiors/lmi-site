# generated using pypi2nix tool (version: 2.0.0)
# See more at: https://github.com/nix-community/pypi2nix
#
# COMMAND:
#   pypi2nix -r requirements.txt -E libmysql -s pytest-runner
#

{ pkgs ? import <nixpkgs> {},
  overrides ? ({ pkgs, python }: self: super: {})
}:

let

  inherit (pkgs) makeWrapper;
  inherit (pkgs.stdenv.lib) fix' extends inNixShell;

  pythonPackages =
  import "${toString pkgs.path}/pkgs/top-level/python-packages.nix" {
    inherit pkgs;
    inherit (pkgs) stdenv;
    python = pkgs.python3;
  };

  commonBuildInputs = with pkgs; [ libmysql ];
  commonDoCheck = false;

  withPackages = pkgs':
    let
      pkgs = builtins.removeAttrs pkgs' ["__unfix__"];
      interpreterWithPackages = selectPkgsFn: pythonPackages.buildPythonPackage {
        name = "python3-interpreter";
        buildInputs = [ makeWrapper ] ++ (selectPkgsFn pkgs);
        buildCommand = ''
          mkdir -p $out/bin
          ln -s ${pythonPackages.python.interpreter} \
              $out/bin/${pythonPackages.python.executable}
          for dep in ${builtins.concatStringsSep " "
              (selectPkgsFn pkgs)}; do
            if [ -d "$dep/bin" ]; then
              for prog in "$dep/bin/"*; do
                if [ -x "$prog" ] && [ -f "$prog" ]; then
                  ln -s $prog $out/bin/`basename $prog`
                fi
              done
            fi
          done
          for prog in "$out/bin/"*; do
            wrapProgram "$prog" --prefix PYTHONPATH : "$PYTHONPATH"
          done
          pushd $out/bin
          ln -s ${pythonPackages.python.executable} python
          ln -s ${pythonPackages.python.executable} \
              python3
          popd
        '';
        passthru.interpreter = pythonPackages.python;
      };

      interpreter = interpreterWithPackages builtins.attrValues;
    in {
      __old = pythonPackages;
      inherit interpreter;
      inherit interpreterWithPackages;
      mkDerivation = args: pythonPackages.buildPythonPackage (args // {
        nativeBuildInputs = (args.nativeBuildInputs or []) ++ args.buildInputs;
      });
      packages = pkgs;
      overrideDerivation = drv: f:
        pythonPackages.buildPythonPackage (
          drv.drvAttrs // f drv.drvAttrs // { meta = drv.meta; }
        );
      withPackages = pkgs'':
        withPackages (pkgs // pkgs'');
    };

  python = withPackages {};

  generated = self: {
    "aniso8601" = python.mkDerivation {
      name = "aniso8601-7.0.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/7f/39/0da0982a3a42fd896beaa07425692fb3100a9d0e40723783efc20f1dec7c/aniso8601-7.0.0.tar.gz";
        sha256 = "513d2b6637b7853806ae79ffaca6f3e8754bdd547048f5ccc1420aec4b714f1e";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://bitbucket.org/nielsenb/aniso8601";
        license = "UNKNOWN";
        description = "A library for parsing ISO 8601 strings.";
      };
    };

    "babel" = python.mkDerivation {
      name = "babel-2.7.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/bd/78/9fb975cbb3f4b136de2cd4b5e5ce4a3341169ebf4c6c03630996d05428f1/Babel-2.7.0.tar.gz";
        sha256 = "e86135ae101e31e2c8ec20a4e0c5220f4eed12487d5cf3f78be7e98d3a57fc28";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."pytz"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://babel.pocoo.org/";
        license = licenses.bsdOriginal;
        description = "Internationalization utilities";
      };
    };

    "cachetools" = python.mkDerivation {
      name = "cachetools-3.1.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/ae/37/7fd45996b19200e0cb2027a0b6bef4636951c4ea111bfad36c71287247f6/cachetools-3.1.1.tar.gz";
        sha256 = "8ea2d3ce97850f31e4a08b0e2b5e6c34997d7216a9d2c98e0f3978630d4da69a";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/tkem/cachetools";
        license = licenses.mit;
        description = "Extensible memoizing collections and decorators";
      };
    };

    "certifi" = python.mkDerivation {
      name = "certifi-2019.9.11";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/62/85/7585750fd65599e88df0fed59c74f5075d4ea2fe611deceb95dd1c2fb25b/certifi-2019.9.11.tar.gz";
        sha256 = "e4f3620cfea4f83eedc95b24abd9cd56f3c4b146dd0177e83a21b4eb49e21e50";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://certifi.io/";
        license = licenses.mpl20;
        description = "Python package for providing Mozilla's CA Bundle.";
      };
    };

    "chardet" = python.mkDerivation {
      name = "chardet-3.0.4";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/fc/bb/a5768c230f9ddb03acc9ef3f0d4a3cf93462473795d18e9535498c8f929d/chardet-3.0.4.tar.gz";
        sha256 = "84ab92ed1c4d4f16916e05906b6b75a6c0fb5db821cc65e70cbd64a3e2a5eaae";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/chardet/chardet";
        license = licenses.lgpl3;
        description = "Universal encoding detector for Python 2 and 3";
      };
    };

    "django" = python.mkDerivation {
      name = "django-2.2.5";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/1d/06/79ddea0bfd4e7cd1f9fa4700c8e524820a5263c6fd8bb91db14f1812c17d/Django-2.2.5.tar.gz";
        sha256 = "deb70aa038e59b58593673b15e9a711d1e5ccd941b5973b30750d5d026abfd56";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."pytz"
        self."sqlparse"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://www.djangoproject.com/";
        license = licenses.bsdOriginal;
        description = "A high-level Python Web framework that encourages rapid development and clean, pragmatic design.";
      };
    };

    "django-admin-sortable2" = python.mkDerivation {
      name = "django-admin-sortable2-0.7.3";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/a4/01/bbdef3339a6bdf37cf2c98c1307d62ec909ea5ca29972808f331ae1f9a09/django-admin-sortable2-0.7.3.tar.gz";
        sha256 = "003f4c9e1dc28ec3435f907e9bc953a922eea7e1da28a7242644e6dbc3071f2e";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."django"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/jrief/django-admin-sortable2";
        license = licenses.mit;
        description = "Generic drag-and-drop sorting for the List, the Stacked- and the Tabular-Inlines Views in the Django Admin";
      };
    };

    "django-ckeditor" = python.mkDerivation {
      name = "django-ckeditor-5.7.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/39/08/d2c66151b821b04aa95692832831388798505a47eb231a8694e3da8e4972/django-ckeditor-5.7.1.tar.gz";
        sha256 = "d79fb8248c50f29dc8f143e5ff7223bb4a916f14ffba6c3fcd998c6d986ad592";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."django-js-asset"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/django-ckeditor/django-ckeditor";
        license = "UNKNOWN";
        description = "Django admin CKEditor integration.";
      };
    };

    "django-js-asset" = python.mkDerivation {
      name = "django-js-asset-1.2.2";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/81/d9/bbb15cf960142220a7a5ca38f2cbddd3ef6ad19f9efc6024670d44b43968/django-js-asset-1.2.2.tar.gz";
        sha256 = "c163ae80d2e0b22d8fb598047cd0dcef31f81830e127cfecae278ad574167260";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/matthiask/django-js-asset/";
        license = licenses.bsdOriginal;
        description = "script tag with additional attributes for django.forms.Media";
      };
    };

    "django-phonenumber-field" = python.mkDerivation {
      name = "django-phonenumber-field-3.0.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/74/c9/112f123cc4c6d19a4132bdcb80d7783e4efaf1517db1f6ce6474fc3d6680/django-phonenumber-field-3.0.1.tar.gz";
        sha256 = "794ebbc3068a7af75aa72a80cb0cec67e714ff8409a965968040f1fd210b2d97";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."babel"
        self."django"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/stefanfoulis/django-phonenumber-field";
        license = licenses.bsdOriginal;
        description = "An international phone number field for django models.";
      };
    };

    "django-solo" = python.mkDerivation {
      name = "django-solo-1.1.3";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/37/49/19e3b15296f545993ce27f2d2ea6526229d18effb1aeeaf3efaead4fe426/django-solo-1.1.3.tar.gz";
        sha256 = "b1206b9a9411b19a4354f7d7d245909a9ea7e9cd566b594363b5adce7dc13e5d";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = "";
        description = "django-solo helps working with singletons: things like global settings that you want to edit from the admin site.";
      };
    };

    "django-tinymce" = python.mkDerivation {
      name = "django-tinymce-2.8.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/96/3b/ea59033ce6fabb61581d857b3e94af9c688d5fe5f599275576c462121f9b/django-tinymce-2.8.0.tar.gz";
        sha256 = "bb7311a2ce705a0b95f4ae8fab4f17445982719b557f4e935d68dae514f7df0a";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/aljosa/django-tinymce";
        license = licenses.mit;
        description = "A Django application that contains a widget to render a form field as a TinyMCE editor.";
      };
    };

    "google-api-python-client" = python.mkDerivation {
      name = "google-api-python-client-1.7.11";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/5e/19/9fd511734c0dee8fa3d49f4109c75e7f95d3c31ed76c0e4a93fbba147807/google-api-python-client-1.7.11.tar.gz";
        sha256 = "a8a88174f66d92aed7ebbd73744c2c319b4b1ce828e565f9ec721352d2e2fb8c";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."google-auth"
        self."google-auth-httplib2"
        self."httplib2"
        self."six"
        self."uritemplate"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://github.com/google/google-api-python-client/";
        license = licenses.asl20;
        description = "Google API Client Library for Python";
      };
    };

    "google-auth" = python.mkDerivation {
      name = "google-auth-1.6.3";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/ef/77/eb1d3288dbe2ba6f4fe50b9bb41770bac514cd2eb91466b56d44a99e2f8d/google-auth-1.6.3.tar.gz";
        sha256 = "0f7c6a64927d34c1a474da92cfc59e552a5d3b940d3266606c6a28b72888b9e4";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."cachetools"
        self."pyasn1-modules"
        self."rsa"
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/GoogleCloudPlatform/google-auth-library-python";
        license = licenses.asl20;
        description = "Google Authentication Library";
      };
    };

    "google-auth-httplib2" = python.mkDerivation {
      name = "google-auth-httplib2-0.0.3";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/e7/32/ac7f30b742276b4911a1439c5291abab1b797ccfd30bc923c5ad67892b13/google-auth-httplib2-0.0.3.tar.gz";
        sha256 = "098fade613c25b4527b2c08fa42d11f3c2037dda8995d86de0745228e965d445";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."google-auth"
        self."httplib2"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/GoogleCloudPlatform/google-auth-library-python-httplib2";
        license = licenses.asl20;
        description = "Google Authentication Library: httplib2 transport";
      };
    };

    "google-auth-oauthlib" = python.mkDerivation {
      name = "google-auth-oauthlib-0.4.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/1b/81/ab7bd0a5286277b37e25da5577a4c8d0085ebbe82784e4f08c4d6ac767ee/google-auth-oauthlib-0.4.0.tar.gz";
        sha256 = "6a8b0072048940d1f41c23c03576867e577e826fec140a1c7e148ec486e083ba";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."google-auth"
        self."requests-oauthlib"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/GoogleCloudPlatform/google-auth-library-python-oauthlib";
        license = licenses.asl20;
        description = "Google Authentication Library";
      };
    };

    "graphene" = python.mkDerivation {
      name = "graphene-2.1.8";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/53/49/3533ea1317a3d32d6ddf9cfa55df6883394195d40b88eb7589d665df887c/graphene-2.1.8.tar.gz";
        sha256 = "2cbe6d4ef15cfc7b7805e0760a0e5b80747161ce1b0f990dfdc0d2cf497c12f9";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."aniso8601"
        self."graphql-core"
        self."graphql-relay"
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphene";
        license = licenses.mit;
        description = "GraphQL Framework for Python";
      };
    };

    "graphene-django" = python.mkDerivation {
      name = "graphene-django-2.5.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/a0/b9/231b5454a7ff28691f85065fdc08aa918a943bdcd6a0ddd144919ab8d1dd/graphene-django-2.5.0.tar.gz";
        sha256 = "25f2bdf41e30bc7b860c1c13bfb4ba5c3961712394f16e847d79a69fc25a06b1";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."django"
        self."graphene"
        self."graphql-core"
        self."promise"
        self."singledispatch"
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphene-django";
        license = licenses.mit;
        description = "Graphene Django integration";
      };
    };

    "graphql-core" = python.mkDerivation {
      name = "graphql-core-2.2.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/98/9b/7a610ac16df594e18263db0404367bd1523127cf7f280285b0f7765be89c/graphql-core-2.2.1.tar.gz";
        sha256 = "da64c472d720da4537a2e8de8ba859210b62841bd47a9be65ca35177f62fe0e4";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."promise"
        self."rx"
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphql-core";
        license = licenses.mit;
        description = "GraphQL implementation for Python";
      };
    };

    "graphql-relay" = python.mkDerivation {
      name = "graphql-relay-2.0.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/a0/83/bea0cd12b51e1459d6702b0975d2f42ae4607021f22ec90c50b03c397fcc/graphql-relay-2.0.0.tar.gz";
        sha256 = "7fa74661246e826ef939ee92e768f698df167a7617361ab399901eaebf80dce6";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."graphql-core"
        self."promise"
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/graphql-python/graphql-relay-py";
        license = licenses.mit;
        description = "Relay implementation for Python";
      };
    };

    "gunicorn" = python.mkDerivation {
      name = "gunicorn-19.9.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/47/52/68ba8e5e8ba251e54006a49441f7ccabca83b6bef5aedacb4890596c7911/gunicorn-19.9.0.tar.gz";
        sha256 = "fa2662097c66f920f53f70621c6c58ca4a3c4d3434205e608e121b5b3b71f4f3";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://gunicorn.org";
        license = licenses.mit;
        description = "WSGI HTTP Server for UNIX";
      };
    };

    "httplib2" = python.mkDerivation {
      name = "httplib2-0.13.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/78/23/bb9606e87a66fd8c72a2b1a75b049d3859a122bc2648915be845bc44e04f/httplib2-0.13.1.tar.gz";
        sha256 = "6901c8c0ffcf721f9ce270ad86da37bc2b4d32b8802d4a9cec38274898a64044";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/httplib2/httplib2";
        license = licenses.mit;
        description = "A comprehensive HTTP client library.";
      };
    };

    "idna" = python.mkDerivation {
      name = "idna-2.8";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/ad/13/eb56951b6f7950cadb579ca166e448ba77f9d24efc03edd7e55fa57d04b7/idna-2.8.tar.gz";
        sha256 = "c357b3f628cf53ae2c4c05627ecc484553142ca23264e593d327bcde5e9c3407";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/kjd/idna";
        license = licenses.bsdOriginal;
        description = "Internationalized Domain Names in Applications (IDNA)";
      };
    };

    "mysqlclient" = python.mkDerivation {
      name = "mysqlclient-1.4.4";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/4d/38/c5f8bac9c50f3042c8f05615f84206f77f03db79781db841898fde1bb284/mysqlclient-1.4.4.tar.gz";
        sha256 = "9c737cc55a5dc8dd3583a942d5a9b21be58d16f00f5fefca4e575e7d9682e98c";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/PyMySQL/mysqlclient-python";
        license = "GPL";
        description = "Python interface to MySQL";
      };
    };

    "oauthlib" = python.mkDerivation {
      name = "oauthlib-3.1.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/fc/c7/829c73c64d3749da7811c06319458e47f3461944da9d98bb4df1cb1598c2/oauthlib-3.1.0.tar.gz";
        sha256 = "bee41cc35fcca6e988463cacc3bcb8a96224f470ca547e697b604cc697b2f889";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/oauthlib/oauthlib";
        license = licenses.bsdOriginal;
        description = "A generic, spec-compliant, thorough implementation of the OAuth request-signing logic";
      };
    };

    "phonenumbers" = python.mkDerivation {
      name = "phonenumbers-8.10.19";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/1d/4a/999514887ca759f44890d36d5c73685d6d2ee28bcdb286e8c671d1bc79c7/phonenumbers-8.10.19.tar.gz";
        sha256 = "fcd9d155af20dbe9a2ecd84ba6df82501ab358f70388ac78e0b3b2dd9523b275";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/daviddrysdale/python-phonenumbers";
        license = licenses.asl20;
        description = "Python version of Google's common library for parsing, formatting, storing and validating international phone numbers.";
      };
    };

    "promise" = python.mkDerivation {
      name = "promise-2.2.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/5a/81/221d09d90176fd90aed4b530e31b8fedf207385767c06d1d46c550c5e418/promise-2.2.1.tar.gz";
        sha256 = "348f5f6c3edd4fd47c9cd65aed03ac1b31136d375aa63871a57d3e444c85655c";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/syrusakbary/promise";
        license = licenses.mit;
        description = "Promises/A+ implementation for Python";
      };
    };

    "pyasn1" = python.mkDerivation {
      name = "pyasn1-0.4.7";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/ca/f8/2a60a2c88a97558bdd289b6dc9eb75b00bd90ff34155d681ba6dbbcb46b2/pyasn1-0.4.7.tar.gz";
        sha256 = "a9495356ca1d66ed197a0f72b41eb1823cf7ea8b5bd07191673e8147aecf8604";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/etingof/pyasn1";
        license = licenses.bsdOriginal;
        description = "ASN.1 types and codecs";
      };
    };

    "pyasn1-modules" = python.mkDerivation {
      name = "pyasn1-modules-0.2.6";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/f1/a9/a1ef72a0e43feff643cf0130a08123dea76205e7a0dda37e3efb5f054a31/pyasn1-modules-0.2.6.tar.gz";
        sha256 = "43c17a83c155229839cc5c6b868e8d0c6041dba149789b6d6e28801c64821722";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."pyasn1"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/etingof/pyasn1-modules";
        license = "BSD-2-Clause";
        description = "A collection of ASN.1-based protocols modules.";
      };
    };

    "pytest-runner" = python.mkDerivation {
      name = "pytest-runner-5.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/d9/6d/4b41a74b31720e25abd4799be72d54811da4b4d0233e38b75864dcc1f7ad/pytest-runner-5.1.tar.gz";
        sha256 = "25a013c8d84f0ca60bb01bd11913a3bcab420f601f0f236de4423074af656e7a";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [
        self."setuptools-scm"
      ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/pytest-dev/pytest-runner/";
        license = "UNKNOWN";
        description = "Invoke py.test as distutils command with dependency resolution";
      };
    };

    "python-dateutil" = python.mkDerivation {
      name = "python-dateutil-2.8.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/ad/99/5b2e99737edeb28c71bcbec5b5dda19d0d9ef3ca3e92e3e925e7c0bb364c/python-dateutil-2.8.0.tar.gz";
        sha256 = "c89805f6f4d64db21ed966fda138f8a5ed7a4fdbc1a8ee329ce1b74e3c74da9e";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [
        self."setuptools-scm"
      ];
      propagatedBuildInputs = [
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://dateutil.readthedocs.io";
        license = "Dual License";
        description = "Extensions to the standard Python datetime module";
      };
    };

    "pytz" = python.mkDerivation {
      name = "pytz-2019.2";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/27/c0/fbd352ca76050952a03db776d241959d5a2ee1abddfeb9e2a53fdb489be4/pytz-2019.2.tar.gz";
        sha256 = "26c0b32e437e54a18161324a2fca3c4b9846b74a8dccddd843113109e1116b32";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://pythonhosted.org/pytz";
        license = licenses.mit;
        description = "World timezone definitions, modern and historical";
      };
    };

    "requests" = python.mkDerivation {
      name = "requests-2.22.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/01/62/ddcf76d1d19885e8579acb1b1df26a852b03472c0e46d2b959a714c90608/requests-2.22.0.tar.gz";
        sha256 = "11e007a8a2aa0323f5a921e9e6a2d7e4e67d9877e85773fba9ba6419025cbeb4";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."certifi"
        self."chardet"
        self."idna"
        self."urllib3"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://python-requests.org";
        license = licenses.asl20;
        description = "Python HTTP for Humans.";
      };
    };

    "requests-oauthlib" = python.mkDerivation {
      name = "requests-oauthlib-1.2.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/de/a2/f55312dfe2f7a344d0d4044fdfae12ac8a24169dc668bd55f72b27090c32/requests-oauthlib-1.2.0.tar.gz";
        sha256 = "bd6533330e8748e94bf0b214775fed487d309b8b8fe823dc45641ebcd9a32f57";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."oauthlib"
        self."requests"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/requests/requests-oauthlib";
        license = "ISC";
        description = "OAuthlib authentication support for Requests.";
      };
    };

    "rsa" = python.mkDerivation {
      name = "rsa-4.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/cb/d0/8f99b91432a60ca4b1cd478fd0bdf28c1901c58e3a9f14f4ba3dba86b57f/rsa-4.0.tar.gz";
        sha256 = "1a836406405730121ae9823e19c6e806c62bbad73f890574fff50efa4122c487";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."pyasn1"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://stuvel.eu/rsa";
        license = "ASL 2";
        description = "Pure-Python RSA implementation";
      };
    };

    "rx" = python.mkDerivation {
      name = "rx-1.6.1";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/25/d7/9bc30242d9af6a9e9bf65b007c56e17b7dc9c13f86e440b885969b3bbdcf/Rx-1.6.1.tar.gz";
        sha256 = "13a1d8d9e252625c173dc795471e614eadfe1cf40ffc684e08b8fff0d9748c23";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://reactivex.io";
        license = "Apache License";
        description = "Reactive Extensions (Rx) for Python";
      };
    };

    "sentry-sdk" = python.mkDerivation {
      name = "sentry-sdk-0.12.2";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/3c/02/2669f5064699e1630466cf02b2ec72dc1cf575cec37f6b21979017e2167a/sentry-sdk-0.12.2.tar.gz";
        sha256 = "2529ab6f93914d01bcd80b1b16c15a025902350ab19af2033aa5ff797c1600ad";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."certifi"
        self."urllib3"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/getsentry/sentry-python";
        license = licenses.bsdOriginal;
        description = "Python client for Sentry (https://getsentry.com)";
      };
    };

    "setuptools-scm" = python.mkDerivation {
      name = "setuptools-scm-3.3.3";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/83/44/53cad68ce686585d12222e6769682c4bdb9686808d2739671f9175e2938b/setuptools_scm-3.3.3.tar.gz";
        sha256 = "bd25e1fb5e4d603dcf490f1fde40fb4c595b357795674c3e5cb7f6217ab39ea5";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/pypa/setuptools_scm/";
        license = licenses.mit;
        description = "the blessed package to manage your versions by scm tags";
      };
    };

    "singledispatch" = python.mkDerivation {
      name = "singledispatch-3.4.0.3";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/d9/e9/513ad8dc17210db12cb14f2d4d190d618fb87dd38814203ea71c87ba5b68/singledispatch-3.4.0.3.tar.gz";
        sha256 = "5b06af87df13818d14f08a028e42f566640aef80805c3b50c5056b086e3c2b9c";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [
        self."six"
      ];
      meta = with pkgs.stdenv.lib; {
        homepage = "http://docs.python.org/3/library/functools.html#functools.singledispatch";
        license = licenses.mit;
        description = "This library brings functools.singledispatch from Python 3.4 to Python 2.6-3.3.";
      };
    };

    "six" = python.mkDerivation {
      name = "six-1.12.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/dd/bf/4138e7bfb757de47d1f4b6994648ec67a51efe58fa907c1e11e350cddfca/six-1.12.0.tar.gz";
        sha256 = "d16a0141ec1a18405cd4ce8b4613101da75da0e9a7aec5bdd4fa804d0e0eba73";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/benjaminp/six";
        license = licenses.mit;
        description = "Python 2 and 3 compatibility utilities";
      };
    };

    "sqlparse" = python.mkDerivation {
      name = "sqlparse-0.3.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/63/c8/229dfd2d18663b375975d953e2bdc06d0eed714f93dcb7732f39e349c438/sqlparse-0.3.0.tar.gz";
        sha256 = "7c3dca29c022744e95b547e867cee89f4fce4373f3549ccd8797d8eb52cdb873";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://github.com/andialbrecht/sqlparse";
        license = licenses.bsdOriginal;
        description = "Non-validating SQL parser";
      };
    };

    "uritemplate" = python.mkDerivation {
      name = "uritemplate-3.0.0";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/cd/db/f7b98cdc3f81513fb25d3cbe2501d621882ee81150b745cdd1363278c10a/uritemplate-3.0.0.tar.gz";
        sha256 = "c02643cebe23fc8adb5e6becffe201185bf06c40bda5c0b4028a93f1527d011d";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://uritemplate.readthedocs.org";
        license = "BSD 3-Clause License or Apache License, Version 2.0";
        description = "URI templates";
      };
    };

    "urllib3" = python.mkDerivation {
      name = "urllib3-1.25.5";
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/3c/31/aa26375d7028397ffa46765f91f5ccb087d37a99437b78259eb46f275f5b/urllib3-1.25.5.tar.gz";
        sha256 = "2f3eadfea5d92bc7899e75b5968410b749a054b492d5a6379c1344a1481bc2cb";
};
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs ++ [ ];
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "https://urllib3.readthedocs.io/";
        license = licenses.mit;
        description = "HTTP library with thread-safe connection pooling, file post, and more.";
      };
    };
  };
  localOverridesFile = ./requirements_override.nix;
  localOverrides = import localOverridesFile { inherit pkgs python; };
  commonOverrides = [
    
  ];
  paramOverrides = [
    (overrides { inherit pkgs python; })
  ];
  allOverrides =
    (if (builtins.pathExists localOverridesFile)
     then [localOverrides] else [] ) ++ commonOverrides ++ paramOverrides;

in python.withPackages
   (fix' (pkgs.lib.fold
            extends
            generated
            allOverrides
         )
   )