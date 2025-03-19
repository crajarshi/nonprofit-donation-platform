import { ChakraProvider } from '@chakra-ui/react';
import type { AppProps } from 'next/app';
import { AuthProvider } from '../hooks/useAuth';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ChakraProvider>
      <AuthProvider>
        <Component {...pageProps} />
      </AuthProvider>
    </ChakraProvider>
  );
} 