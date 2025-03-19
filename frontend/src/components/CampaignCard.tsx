import { Box, Image, Badge, Text, Progress, Button, VStack, HStack, useColorModeValue } from '@chakra-ui/react';
import { useRouter } from 'next/router';

interface Campaign {
  id: number;
  title: string;
  description: string;
  target_amount: number;
  current_amount: number;
  end_date: string;
  image_url: string;
  npo: {
    name: string;
    is_verified: boolean;
  };
}

interface CampaignCardProps {
  campaign: Campaign;
}

const CampaignCard = ({ campaign }: CampaignCardProps) => {
  const router = useRouter();
  const cardBg = useColorModeValue('white', 'gray.700');
  const progressColor = useColorModeValue('teal.500', 'teal.200');

  const progress = (campaign.current_amount / campaign.target_amount) * 100;
  const daysLeft = Math.max(0, Math.ceil((new Date(campaign.end_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)));

  return (
    <Box
      bg={cardBg}
      borderRadius="lg"
      overflow="hidden"
      boxShadow="md"
      transition="transform 0.2s"
      _hover={{ transform: 'translateY(-4px)' }}
    >
      <Image
        src={campaign.image_url || '/default-campaign.jpg'}
        alt={campaign.title}
        height="200px"
        width="100%"
        objectFit="cover"
      />

      <VStack p={5} align="stretch" spacing={4}>
        <HStack justify="space-between">
          <Text fontSize="sm" color="gray.500">
            {campaign.npo.name}
          </Text>
          {campaign.npo.is_verified && (
            <Badge colorScheme="green">Verified</Badge>
          )}
        </HStack>

        <Text fontSize="xl" fontWeight="semibold" noOfLines={2}>
          {campaign.title}
        </Text>

        <Text noOfLines={3} color="gray.500">
          {campaign.description}
        </Text>

        <Box>
          <HStack justify="space-between" mb={2}>
            <Text fontWeight="bold">
              {campaign.current_amount} XRP
            </Text>
            <Text color="gray.500">
              of {campaign.target_amount} XRP
            </Text>
          </HStack>
          <Progress
            value={progress}
            colorScheme="teal"
            size="sm"
            borderRadius="full"
          />
        </Box>

        <HStack justify="space-between">
          <Text fontSize="sm" color="gray.500">
            {daysLeft} days left
          </Text>
          <Button
            colorScheme="teal"
            size="sm"
            onClick={() => router.push(`/campaigns/${campaign.id}`)}
          >
            Donate Now
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
};

export default CampaignCard; 