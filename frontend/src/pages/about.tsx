import {
  Box,
  Container,
  Heading,
  Text,
  Stack,
  Avatar,
  SimpleGrid,
  useColorModeValue,
} from '@chakra-ui/react';
import Layout from '../components/Layout';

const TeamMember = ({ name, role, image }: { name: string; role: string; image: string }) => {
  return (
    <Stack align={'center'} textAlign={'center'}>
      <Avatar size={'xl'} src={image} mb={4} />
      <Text fontWeight={600}>{name}</Text>
      <Text color={'gray.600'}>{role}</Text>
    </Stack>
  );
};

export default function About() {
  return (
    <Layout>
      <Container maxW={'7xl'} py={20}>
        <Stack spacing={12}>
          {/* Mission Section */}
          <Stack spacing={4} as={Container} maxW={'3xl'} textAlign={'center'}>
            <Heading fontSize={'4xl'}>Our Mission</Heading>
            <Text color={'gray.600'} fontSize={'xl'}>
              We're dedicated to making charitable giving more transparent, efficient,
              and impactful. Our platform connects donors with verified nonprofits,
              ensuring that every contribution makes a real difference.
            </Text>
          </Stack>

          {/* Values Section */}
          <Box>
            <Stack spacing={4} as={Container} maxW={'3xl'} textAlign={'center'} mb={8}>
              <Heading fontSize={'3xl'}>Our Values</Heading>
            </Stack>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10}>
              <Box p={5} shadow={'md'} borderWidth={'1px'} borderRadius={'lg'}>
                <Heading fontSize={'xl'} mb={4}>Transparency</Heading>
                <Text color={'gray.600'}>
                  We believe in complete transparency in charitable giving. Every
                  donation is tracked and verified, giving you peace of mind about
                  where your money goes.
                </Text>
              </Box>
              <Box p={5} shadow={'md'} borderWidth={'1px'} borderRadius={'lg'}>
                <Heading fontSize={'xl'} mb={4}>Trust</Heading>
                <Text color={'gray.600'}>
                  We carefully verify all nonprofits on our platform to ensure they
                  meet our strict standards for accountability and impact.
                </Text>
              </Box>
              <Box p={5} shadow={'md'} borderWidth={'1px'} borderRadius={'lg'}>
                <Heading fontSize={'xl'} mb={4}>Impact</Heading>
                <Text color={'gray.600'}>
                  We focus on maximizing the impact of every donation by minimizing
                  fees and ensuring funds reach their intended recipients quickly.
                </Text>
              </Box>
            </SimpleGrid>
          </Box>

          {/* Team Section */}
          <Box>
            <Stack spacing={4} as={Container} maxW={'3xl'} textAlign={'center'} mb={8}>
              <Heading fontSize={'3xl'}>Our Team</Heading>
              <Text color={'gray.600'} fontSize={'xl'}>
                Meet the passionate individuals behind our mission to revolutionize
                charitable giving.
              </Text>
            </Stack>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10} px={8}>
              <TeamMember
                name="Sarah Johnson"
                role="Executive Director"
                image="/team/sarah.jpg"
              />
              <TeamMember
                name="Michael Chen"
                role="Technical Lead"
                image="/team/michael.jpg"
              />
              <TeamMember
                name="Emily Rodriguez"
                role="Nonprofit Relations"
                image="/team/emily.jpg"
              />
            </SimpleGrid>
          </Box>
        </Stack>
      </Container>
    </Layout>
  );
} 