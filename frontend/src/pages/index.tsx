import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  Stack,
  SimpleGrid,
  Icon,
  useColorModeValue,
} from '@chakra-ui/react';
import { FaHandHoldingHeart, FaUsers, FaChartLine } from 'react-icons/fa';
import NextLink from 'next/link';
import Layout from '../components/Layout';

const Feature = ({ title, text, icon }: { title: string; text: string; icon: any }) => {
  return (
    <Stack align={'center'} textAlign={'center'}>
      <Icon as={icon} w={10} h={10} color="teal.500" />
      <Text fontWeight={600}>{title}</Text>
      <Text color={'gray.600'}>{text}</Text>
    </Stack>
  );
};

export default function Home() {
  return (
    <Layout>
      <Box>
        {/* Hero Section */}
        <Box
          bg={useColorModeValue('gray.50', 'gray.900')}
          color={useColorModeValue('gray.700', 'gray.200')}
        >
          <Container maxW={'7xl'} py={{ base: 20, md: 28 }}>
            <Stack
              align={'center'}
              spacing={{ base: 8, md: 10 }}
              textAlign={'center'}
            >
              <Heading
                fontWeight={600}
                fontSize={{ base: '3xl', sm: '4xl', md: '6xl' }}
                lineHeight={'110%'}
              >
                Making a difference{' '}
                <Text as={'span'} color={'teal.400'}>
                  made easy
                </Text>
              </Heading>
              <Text color={'gray.500'} maxW={'3xl'}>
                Join our platform to support meaningful causes and make a real impact.
                Connect with verified nonprofits, track your donations, and see the
                difference you're making in the world.
              </Text>
              <Stack spacing={6} direction={'row'}>
                <Button
                  as={NextLink}
                  href="/campaigns"
                  rounded={'full'}
                  px={6}
                  colorScheme={'teal'}
                  bg={'teal.400'}
                  _hover={{ bg: 'teal.500' }}
                >
                  Browse Campaigns
                </Button>
                <Button
                  as={NextLink}
                  href="/about"
                  rounded={'full'}
                  px={6}
                >
                  Learn More
                </Button>
              </Stack>
            </Stack>
          </Container>
        </Box>

        {/* Features Section */}
        <Container maxW={'7xl'} py={20}>
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10}>
            <Feature
              icon={FaHandHoldingHeart}
              title={'Trusted Platform'}
              text={'We verify all nonprofits to ensure your donations go to legitimate causes.'}
            />
            <Feature
              icon={FaUsers}
              title={'Community Impact'}
              text={'Join thousands of donors making a difference in communities worldwide.'}
            />
            <Feature
              icon={FaChartLine}
              title={'Transparent Tracking'}
              text={'Track your donations and see the direct impact of your contributions.'}
            />
          </SimpleGrid>
        </Container>
      </Box>
    </Layout>
  );
} 