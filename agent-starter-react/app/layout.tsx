import { Public_Sans } from 'next/font/google';
import localFont from 'next/font/local';
import { headers } from 'next/headers';
import { APP_CONFIG_DEFAULTS } from '@/app-config';
import { ApplyThemeScript, ThemeToggle } from '@/components/theme-toggle';
import { getAppConfig } from '@/lib/utils';
import './globals.css';

const publicSans = Public_Sans({
  variable: '--font-public-sans',
  subsets: ['latin'],
});

const commitMono = localFont({
  src: [
    {
      path: './fonts/CommitMono-400-Regular.otf',
      weight: '400',
      style: 'normal',
    },
    {
      path: './fonts/CommitMono-700-Regular.otf',
      weight: '700',
      style: 'normal',
    },
    {
      path: './fonts/CommitMono-400-Italic.otf',
      weight: '400',
      style: 'italic',
    },
    {
      path: './fonts/CommitMono-700-Italic.otf',
      weight: '700',
      style: 'italic',
    },
  ],
  variable: '--font-commit-mono',
});

interface RootLayoutProps {
  children: React.ReactNode;
}

export default async function RootLayout({ children }: RootLayoutProps) {
  const hdrs = await headers();

  const {
    accent,
    accentDark,
    pageTitle,
    pageDescription,
  } = await getAppConfig(hdrs);

  const styles = [
    process.env.NODE_ENV === 'development' || accent !== APP_CONFIG_DEFAULTS.accent
      ? `:root {
          --primary: ${accent};
          --primary-hover: color-mix(in srgb, ${accent} 80%, #000);
        }`
      : '',

    process.env.NODE_ENV === 'development' || accentDark !== APP_CONFIG_DEFAULTS.accentDark
      ? `.dark {
          --primary: ${accentDark};
          --primary-hover: color-mix(in srgb, ${accentDark} 80%, #000);
        }`
      : '',
  ]
    .filter(Boolean)
    .join('\n');

  return (
    <html
      lang="en"
      suppressHydrationWarning
      className="light scroll-smooth"
    >
      <head>
        {styles && <style>{styles}</style>}

        <title>{pageTitle}</title>
        <meta
          name="description"
          content={pageDescription}
        />

        {/* Force light mode on first load */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              document.documentElement.classList.remove('dark');
              document.documentElement.classList.add('light');
            `,
          }}
        />

   {/* <ApplyThemeScript /> */}
      </head>

      <body
        className={`
          ${publicSans.variable}
          ${commitMono.variable}
          overflow-x-hidden
          antialiased
          bg-white
          text-black
          min-h-screen
        `}
      >
        {children}

        <div className="group fixed bottom-0 left-1/2 z-50 mb-2 -translate-x-1/2">
          <ThemeToggle className="translate-y-20 transition-transform delay-150 duration-300 group-hover:translate-y-0" />
        </div>
      </body>
    </html>
  );
}