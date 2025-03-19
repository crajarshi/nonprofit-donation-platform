import { ReactNode } from 'react';
import {
  Box,
  Flex,
  HStack,
  Link,
  IconButton,
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
  useColorModeValue,
  Stack,
  useColorMode,
} from '@chakra-ui/react';
import { HamburgerIcon, CloseIcon, MoonIcon, SunIcon } from '@chakra-ui/icons';
import NextLink from 'next/link';
import { useAuth } from '../hooks/useAuth';

const NavLink = ({ children, href }: { children: ReactNode; href: string }) => (
  <Link
    as={NextLink}
    px={2}
    py={1}
    rounded={'md'}
    _hover={{
      textDecoration: 'none',
      bg: useColorModeValue('gray.200', 'gray.700'),
    }}
    href={href}
  >
    {children}
  </Link>
);

export default function Layout({ children }: { children: ReactNode }) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { colorMode, toggleColorMode } = useColorMode();
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <Box minH="100vh">
      <Box bg={useColorModeValue('white', 'gray.900')} px={4} boxShadow="sm">
        <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
          <IconButton
            size={'md'}
            icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
            aria-label={'Open Menu'}
            display={{ md: 'none' }}
            onClick={isOpen ? onClose : onOpen}
          />
          <HStack spacing={8} alignItems={'center'}>
            <Box fontWeight="bold">
              <Link as={NextLink} href="/" _hover={{ textDecoration: 'none' }}>
                NonProfit Platform
              </Link>
            </Box>
            <HStack as={'nav'} spacing={4} display={{ base: 'none', md: 'flex' }}>
              <NavLink href="/campaigns">Campaigns</NavLink>
              <NavLink href="/npos">Organizations</NavLink>
              <NavLink href="/about">About</NavLink>
            </HStack>
          </HStack>
          <Flex alignItems={'center'}>
            <Stack direction={'row'} spacing={7}>
              <Button onClick={toggleColorMode}>
                {colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              </Button>

              {isAuthenticated ? (
                <Menu>
                  <MenuButton
                    as={Button}
                    rounded={'full'}
                    variant={'link'}
                    cursor={'pointer'}
                    minW={0}
                  >
                    {user?.full_name || user?.email}
                  </MenuButton>
                  <MenuList>
                    <MenuItem as={NextLink} href="/dashboard">
                      Dashboard
                    </MenuItem>
                    <MenuItem as={NextLink} href="/profile">
                      Profile
                    </MenuItem>
                    <MenuItem onClick={logout}>Sign Out</MenuItem>
                  </MenuList>
                </Menu>
              ) : (
                <Stack direction={'row'} spacing={4}>
                  <Button as={NextLink} href="/login" variant={'ghost'}>
                    Sign In
                  </Button>
                  <Button
                    as={NextLink}
                    href="/signup"
                    colorScheme={'teal'}
                    variant={'solid'}
                  >
                    Sign Up
                  </Button>
                </Stack>
              )}
            </Stack>
          </Flex>
        </Flex>

        {isOpen ? (
          <Box pb={4} display={{ md: 'none' }}>
            <Stack as={'nav'} spacing={4}>
              <NavLink href="/campaigns">Campaigns</NavLink>
              <NavLink href="/npos">Organizations</NavLink>
              <NavLink href="/about">About</NavLink>
            </Stack>
          </Box>
        ) : null}
      </Box>

      <Box as="main">
        {children}
      </Box>

      <Box
        as="footer"
        bg={useColorModeValue('gray.50', 'gray.900')}
        color={useColorModeValue('gray.700', 'gray.200')}
        mt="auto"
        py={10}
      >
        <Flex
          direction={{ base: 'column', md: 'row' }}
          maxW="container.xl"
          mx="auto"
          px={8}
          align="center"
          justify="space-between"
        >
          <Box>© 2024 NonProfit Platform. All rights reserved.</Box>
          <HStack spacing={4} mt={{ base: 4, md: 0 }}>
            <Link href="/privacy">Privacy Policy</Link>
            <Link href="/terms">Terms of Service</Link>
            <Link href="/contact">Contact</Link>
          </HStack>
        </Flex>
      </Box>
    </Box>
  );
} 