from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Generator


if TYPE_CHECKING:
    from beagle.transformer.base_transformer import Transformer


class DataSource(object, metaclass=ABCMeta):
    """Base DataSource class. This class should be used to create DataSources which are file based.

    For non-file based data sources (i.e performing a HTTP request to an API to get some data). The
    ExternalDataSource class should be subclassed.

    Each datasource requires the following annotations be made:

        1. name `string`: The name of the datasource, this should be human readable.
        2. transformer `List[Transformer]`:  The list of transformers which you can send events from this datasource to.
        3. category `string`: The category this datasource outputs data to, this should be human readable.

    Not supplying these three will not allow the class to get created, and will prevent beagle from loading.

    Examples
    --------

    >>> class MyDataSource(DataSource):
            name = "My Data Source"
            transformers = [GenericTransformer]
            category = "My Category"

    """

    def __init_subclass__(cls, **kwargs):
        """Validated the subclass has the required annotations.
        """

        # Don't want this to trigger on abstract classes.
        if "ExternalDataSource" in str(cls):
            return

        if "name" not in cls.__dict__:
            raise RuntimeError(f"A DataSource sublcass **must** contain the name annotation")

        if "transformers" not in cls.__dict__:
            raise RuntimeError(
                f"A DataSource sublcass **must** contain the transformers annotation"
            )
        if "category" not in cls.__dict__:
            raise RuntimeError(f"A DataSource sublcass **must** contain the category annotation")
        elif not isinstance(cls.transformers, list):
            raise RuntimeError(f"The tranformers annotation must be a list")

    @abstractmethod
    def events(self) -> Generator[dict, None, None]:
        """Generator which must yield each event as a dictionary from the datasource one by
        one, once the generator is exhausted, this signals the datasource is exhausted.

        Returns
        -------
        Generator[dict, None, None]
            Generator over all events from this datasource.
        """

        raise NotImplementedError()

    @abstractmethod
    def metadata(self) -> dict:
        """Returns the metadata object for this data source.

        Returns
        -------
        dict
            A metadata dictionary to store with the graph.
        """
        raise NotImplementedError()

    def to_transformer(self, transformer: "Transformer" = None) -> "Transformer":
        """Allows the data source to be used as a functional API.

        >>> graph = DataSource().to_transformer().to_graph()

        Returns
        -------
        Transformer
            A instance of the transformer class yielded to.
        """
        if transformer is None:
            transformer_cls = self.transformers[0]  # type: ignore
        else:
            transformer_cls = transformer
        return transformer_cls(self)


class ExternalDataSource(DataSource, metaclass=ABCMeta):
    """This class should be used when fetching data from exteranl sources before processing.

    Using a different class allows the web interface to render a different upload page when
    a data source requiring text input in favor of a file input is used.

    Examples
    --------
    See :py:class:`beagle.datasources.virustotal.generic_vt_sandbox_api.GenericVTSandboxAPI`
    """
