import { afterEach, describe, expect, it, vi } from 'vitest';

describe('main entrypoint', () => {
  afterEach(() => {
    vi.resetModules();
    vi.doUnmock('react-dom/client');
    vi.doUnmock('./App');
    vi.unstubAllGlobals();
  });

  it('mounts App into the root element', async () => {
    const rootElement = { id: 'root' };
    const render = vi.fn();
    const createRoot = vi.fn(() => ({ render }));

    vi.stubGlobal('document', {
      getElementById: vi.fn(() => rootElement),
    });
    vi.doMock('react-dom/client', () => ({ default: { createRoot } }));
    vi.doMock('./App', async () => {
      const React = await vi.importActual<typeof import('react')>('react');
      return { default: () => React.createElement('app-view') };
    });

    await import('./main');

    expect(document.getElementById).toHaveBeenCalledWith('root');
    expect(createRoot).toHaveBeenCalledWith(rootElement);
    expect(render).toHaveBeenCalledOnce();
  });
});
