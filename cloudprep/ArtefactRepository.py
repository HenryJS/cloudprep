import os

class ArtefactRepository:
    __repo_path = "./artefacts"
    __repository = None

    @staticmethod
    def get_repository():
        if ArtefactRepository.__repository is None:
            ArtefactRepository.__repository = ArtefactRepository()
        return ArtefactRepository.__repository

    def __init__(self):
        self._artefacts = []

    def _create_dir(self):
        if not os.path.exists(self.__repo_path):
            os.mkdir(self.__repo_path)

    def store_artefact(self, artefact):
        self._create_dir()
        with open(self.get_local_name(artefact), "wb") as file:
            file.write(artefact.contents)

        self._artefacts.append(artefact)

    def get_local_name(self, artefact):
        return os.path.join(self.__repo_path, artefact.name)