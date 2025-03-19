import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  SimpleGrid,
  Text,
  Select,
  HStack,
  Input,
  InputGroup,
  InputLeftElement,
  Spinner,
  Center,
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';
import { getCampaigns } from '../../api/campaigns';
import CampaignCard from '../../components/CampaignCard';

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all'); // all, active, ended

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        setIsLoading(true);
        setError('');
        const response = await getCampaigns({
          active_only: filter === 'active',
        });
        setCampaigns(response.data);
      } catch (err) {
        setError('Failed to load campaigns. Please try again later.');
        console.error('Error fetching campaigns:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCampaigns();
  }, [filter]);

  const filteredCampaigns = campaigns.filter((campaign) =>
    campaign.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    campaign.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    campaign.npo.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box py={8}>
      <Container maxW="container.xl">
        <Heading mb={8}>Active Campaigns</Heading>

        {/* Search and Filter */}
        <HStack mb={8} spacing={4}>
          <InputGroup maxW="400px">
            <InputLeftElement pointerEvents="none">
              <SearchIcon color="gray.300" />
            </InputLeftElement>
            <Input
              placeholder="Search campaigns..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
          <Select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            maxW="200px"
          >
            <option value="all">All Campaigns</option>
            <option value="active">Active Only</option>
            <option value="ended">Ended</option>
          </Select>
        </HStack>

        {isLoading ? (
          <Center py={10}>
            <Spinner size="xl" color="teal.500" />
          </Center>
        ) : error ? (
          <Text color="red.500" textAlign="center">{error}</Text>
        ) : filteredCampaigns.length === 0 ? (
          <Text textAlign="center">No campaigns found.</Text>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8}>
            {filteredCampaigns.map((campaign) => (
              <CampaignCard key={campaign.id} campaign={campaign} />
            ))}
          </SimpleGrid>
        )}
      </Container>
    </Box>
  );
} 