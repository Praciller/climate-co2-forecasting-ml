import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ThemeProvider, useTheme } from './ThemeProvider'

function ThemeHarness() {
  const { resolvedTheme, setTheme, theme } = useTheme()

  return (
    <div>
      <output data-testid="theme-state">
        {theme}:{resolvedTheme}
      </output>
      <button type="button" onClick={() => setTheme('light')}>
        Set light
      </button>
      <button type="button" onClick={() => setTheme('dark')}>
        Set dark
      </button>
      <button type="button" onClick={() => setTheme('system')}>
        Set system
      </button>
    </div>
  )
}

function renderTheme() {
  return render(
    <ThemeProvider>
      <ThemeHarness />
    </ThemeProvider>,
  )
}

function setMatchMedia(matches: boolean, mode: 'modern' | 'legacy' = 'modern') {
  let listener: ((event: MediaQueryListEvent) => void) | undefined
  const mediaQuery = {
    matches,
    media: '(prefers-color-scheme: dark)',
    onchange: null,
    addEventListener: mode === 'modern' ? vi.fn((_type: string, nextListener: (event: MediaQueryListEvent) => void) => {
      listener = nextListener
    }) : undefined,
    removeEventListener: vi.fn(),
    addListener: vi.fn((nextListener: (event: MediaQueryListEvent) => void) => {
      listener = nextListener
    }),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  } as unknown as MediaQueryList

  vi.stubGlobal('matchMedia', vi.fn(() => mediaQuery))

  return {
    mediaQuery,
    change(nextMatches: boolean) {
      Object.defineProperty(mediaQuery, 'matches', { configurable: true, value: nextMatches })
      listener?.({ matches: nextMatches } as MediaQueryListEvent)
    },
  }
}

describe('ThemeProvider', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.className = ''
    vi.unstubAllGlobals()
  })

  it('defaults to system and resolves the current preference when storage is empty', () => {
    const media = setMatchMedia(true)

    renderTheme()

    expect(screen.getByTestId('theme-state')).toHaveTextContent('system:dark')
    expect(document.documentElement).toHaveClass('dark')
    expect(document.documentElement).not.toHaveClass('light')
    expect(media.mediaQuery.matches).toBe(true)
  })

  it.each([
    ['light', 'light'],
    ['dark', 'dark'],
  ] as const)('applies a saved %s theme class', (stored, resolved) => {
    localStorage.setItem('co2-forecast-lab-theme', stored)
    setMatchMedia(false)

    renderTheme()

    expect(screen.getByTestId('theme-state')).toHaveTextContent(`${stored}:${resolved}`)
    expect(document.documentElement).toHaveClass(resolved)
  })

  it('falls back to system for an invalid stored value', () => {
    localStorage.setItem('co2-forecast-lab-theme', 'sepia')
    setMatchMedia(false)

    renderTheme()

    expect(screen.getByTestId('theme-state')).toHaveTextContent('system:light')
    expect(localStorage.getItem('co2-forecast-lab-theme')).toBe('sepia')
  })

  it.each(['light', 'dark', 'system'] as const)('persists the exact %s value', async (theme) => {
    setMatchMedia(false)
    const user = userEvent.setup()
    renderTheme()

    await user.click(screen.getByRole('button', { name: `Set ${theme}` }))

    expect(localStorage.getItem('co2-forecast-lab-theme')).toBe(theme)
    expect(screen.getByTestId('theme-state')).toHaveTextContent(new RegExp(`^${theme}:`))
  })

  it('updates system mode when the operating-system preference changes', async () => {
    const media = setMatchMedia(false)
    renderTheme()
    const user = userEvent.setup()

    expect(screen.getByTestId('theme-state')).toHaveTextContent('system:light')
    media.change(true)
    await waitFor(() => {
      expect(screen.getByTestId('theme-state')).toHaveTextContent('system:dark')
    })

    await user.click(screen.getByRole('button', { name: 'Set light' }))
    media.change(false)
    await waitFor(() => {
      expect(screen.getByTestId('theme-state')).toHaveTextContent('light:light')
    })
  })

  it('uses the modern media-query listener API once and cleans it up', () => {
    const media = setMatchMedia(false, 'modern')
    const view = renderTheme()

    expect(media.mediaQuery.addEventListener).toHaveBeenCalledTimes(1)
    expect(media.mediaQuery.addListener).not.toHaveBeenCalled()
    view.unmount()
    expect(media.mediaQuery.removeEventListener).toHaveBeenCalledTimes(1)
    expect(media.mediaQuery.removeListener).not.toHaveBeenCalled()
  })

  it('falls back to the legacy media-query listener API and cleans it up', () => {
    const media = setMatchMedia(false, 'legacy')
    const view = renderTheme()

    expect(media.mediaQuery.addEventListener).toBeUndefined()
    expect(media.mediaQuery.addListener).toHaveBeenCalledTimes(1)
    view.unmount()
    expect(media.mediaQuery.removeListener).toHaveBeenCalledTimes(1)
    expect(media.mediaQuery.removeEventListener).not.toHaveBeenCalled()
  })
})
