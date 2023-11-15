import dataclasses
import typing as tp

import typing_extensions as tpe

A = tp.TypeVar('A')


class _ProxyContext(tpe.Protocol):
  def __call__(self, accessor: 'DelayedAccessor', /, *args, **kwargs) -> tp.Any:
    ...


@dataclasses.dataclass
class CallableProxy:
  _proxy_context: _ProxyContext
  _proxy_callable: tp.Callable[..., tp.Any]

  def __call__(self, *args, **kwargs):
    return self._proxy_context(self._proxy_callable, *args, **kwargs)

  def __getattr__(self, name) -> 'CallableProxy':
    return CallableProxy(
      self._proxy_context, getattr(self._proxy_callable, name)
    )

  def __getitem__(self, key) -> 'CallableProxy':
    return CallableProxy(self._proxy_context, self._proxy_callable[key])


def _identity(x):
  return x


@dataclasses.dataclass
class DelayedAccessor:
  accessor: tp.Callable[[tp.Any], tp.Any] = _identity

  def __call__(self, x):
    return self.accessor(x)

  def __getattr__(self, name):
    return DelayedAccessor(lambda x: getattr(x, name))

  def __getitem__(self, key):
    return DelayedAccessor(lambda x: x[key])


class ApplyCaller(tp.Protocol, tp.Generic[A]):
  def __getattr__(self, __name) -> 'ApplyCaller[A]':
    ...

  def __getitem__(self, __name) -> 'ApplyCaller[A]':
    ...

  def __call__(self, *args, **kwargs) -> tuple[tp.Any, A]:
    ...
