#!/user/bin/env python3


class TestResolveUserInstall:

    def test_install_with_user_flag_in_venv(self, make):
        make.resolve_user()
        assert not make.obj["user"]

    def test_inst_user_not_in_venv(self, make):
        make.obj["venv"] = False
        make.resolve_user()
        assert make.obj["user"]

    def test_inst_user_in_venv(self, make):
        make.obj["user"] = False
        make.obj.update({"venv": False, "install": False})
        self.test_install_with_user_flag_in_venv(make)

    def test_resolve_user_none(self, make):
        make.obj.update({"venv": False, "install": False})
        assert make.resolve_user() is None

    def test_uninst_user_in_venv(self, make):
        make.obj["install"] = False
        make.obj.update({"venv": False, "install": False})
        self.test_install_with_user_flag_in_venv(make)

    def test_uninst_user_not_in_venv(self, make, ):
        make.obj.update({"venv": False, "install": False})
        self.test_install_with_user_flag_in_venv(make)
