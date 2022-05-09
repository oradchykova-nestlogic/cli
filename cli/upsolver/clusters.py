from abc import ABCMeta, abstractmethod
from typing import Any

from cli import errors
from cli.upsolver.entities import Cluster
from cli.upsolver.requester import Requester


class RawClustersApi(metaclass=ABCMeta):
    @abstractmethod
    def get_clusters_raw(self) -> list[dict[Any, Any]]:
        pass


class ClustersApi(RawClustersApi):
    @abstractmethod
    def get_clusters(self) -> list[Cluster]:
        pass

    @abstractmethod
    def stop_cluster(self, cluster: str) -> None:
        pass

    @abstractmethod
    def run_cluster(self, cluster: str) -> None:
        pass

    @abstractmethod
    def delete_cluster(self, cluster: str) -> None:
        pass


class RestClustersApi(ClustersApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def _get_cluster_id(self, cluster: str) -> str:
        available_clusters = self.get_clusters()
        for c in available_clusters:
            if c.name == cluster:
                return c.id

        raise errors.EntityNotFound(cluster, [c.name for c in available_clusters])

    def get_clusters(self) -> list[Cluster]:
        return [env.to_cluster() for env in self.requester.get_environments()]

    def get_clusters_raw(self) -> list[dict[Any, Any]]:
        return self.requester.get_list('environments/dashboard')

    def stop_cluster(self, cluster: str) -> None:
        self.requester.put(f'environments/stop/{self._get_cluster_id(cluster)}')

    def run_cluster(self, cluster: str) -> None:
        self.requester.put(f'environments/run/{self._get_cluster_id(cluster)}')

    def delete_cluster(self, cluster: str) -> None:
        self.requester.patch(
            path=f'environments/{self._get_cluster_id(cluster)}',
            json={'clazz': 'DeleteEnvironment'}
        )
