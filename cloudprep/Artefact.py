from .ArtefactRepository import ArtefactRepository

class Artefact:
    def __init__(self, name, contents):
        self._name = name
        self._contents = contents

    @property
    def name(self):
        return self._name

    @property
    def contents(self):
        return self._contents

    @property
    def local_name(self):
        return ArtefactRepository.get_local_path(self)