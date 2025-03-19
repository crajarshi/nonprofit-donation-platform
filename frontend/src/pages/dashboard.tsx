import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { Container, Text, Box, SimpleGrid, VStack } from '@chakra-ui/react';
import { useAuth } from '../hooks/useAuth';

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, router]);

  if (loading) {
    return (
      <Container maxW="container.xl" py={8}>
        <Text>Loading...</Text>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <Box mb={8}>
        <Text fontSize="2xl" fontWeight="bold" mb={6}>
          Dashboard
        </Text>
        <SimpleGrid columns={1} spacing={6}>
          <Box p={6} shadow="md" borderWidth="1px" borderRadius="md">
            <VStack align="stretch" spacing={3}>
              <Text fontSize="xl" fontWeight="semibold">
                Welcome, {user?.full_name}!
              </Text>
              <Text>
                Email: {user?.email}
              </Text>
              {user?.is_nonprofit && (
                <Text mt={2}>
                  You are registered as a nonprofit organization.
                </Text>
              )}
            </VStack>
          </Box>
          {user?.is_nonprofit && (
            <Box p={6} shadow="md" borderWidth="1px" borderRadius="md">
              <VStack align="stretch" spacing={3}>
                <Text fontSize="xl" fontWeight="semibold">
                  Nonprofit Management
                </Text>
                <Text>
                  Manage your nonprofit organization, campaigns, and donations here.
                </Text>
              </VStack>
            </Box>
          )}
          <Box p={6} shadow="md" borderWidth="1px" borderRadius="md">
            <VStack align="stretch" spacing={3}>
              <Text fontSize="xl" fontWeight="semibold">
                Recent Activity
              </Text>
              <Text>
                Your recent donations and activities will appear here.
              </Text>
            </VStack>
          </Box>
        </SimpleGrid>
      </Box>
    </Container>
  );
};

export default Dashboard; 