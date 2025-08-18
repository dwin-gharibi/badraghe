import React from "react";
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Image,
  Icon,
  useColorModeValue,
  keyframes,
} from "@chakra-ui/react";
import { FaPlane, FaTicketAlt, FaGlobe, FaHotel, FaMap, FaMountain, FaShip } from "react-icons/fa";

export default function Cta() {
  const bg = useColorModeValue("brand.500", "brand.400");

  const float = keyframes`
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
  `;
  const floatAnim = `${float} 4s ease-in-out infinite`;

  return (
    <Box
      bgGradient="linear(to-r, brand.500, brand.400)"
      py={{ base: 16, md: 24 }}
      position="relative"
      overflow="hidden"
      color="white"
    >
      {[
        { icon: FaPlane, top: "10%", left: "5%", size: 12, opacity: 0.2, duration: "4s" },
        { icon: FaGlobe, top: "20%", right: "10%", size: 14, opacity: 0.15, duration: "5s" },
        { icon: FaHotel, top: "40%", left: "15%", size: 10, opacity: 0.25, duration: "6s" },
        { icon: FaTicketAlt, top: "60%", right: "20%", size: 12, opacity: 0.2, duration: "7s" },
        { icon: FaMountain, bottom: "10%", left: "10%", size: 16, opacity: 0.1, duration: "5s" },
        { icon: FaMap, bottom: "25%", right: "5%", size: 14, opacity: 0.15, duration: "6s" },
        { icon: FaShip, top: "70%", left: "30%", size: 12, opacity: 0.2, duration: "4s" },
      ].map((item, idx) => (
        <Icon
          key={idx}
          as={item.icon}
          w={item.size}
          h={item.size}
          position="absolute"
          top={item.top}
          bottom={item.bottom}
          left={item.left}
          right={item.right}
          opacity={item.opacity}
          animation={`${float} ${item.duration} ease-in-out infinite`}
        />
      ))}

      <Container maxW="container.xl" position="relative" zIndex={2}>
        <VStack spacing={6} textAlign="center">
          <HStack spacing={4} justify="center">
            <Icon as={FaPlane} w={8} h={8} />
            <Heading size="2xl" fontWeight="extrabold">
              Explore the World with Badraghe Travel
            </Heading>
            <Icon as={FaGlobe} w={8} h={8} />
          </HStack>

          <Text fontSize="lg" maxW="3xl">
            Find the best flights, hotels, and travel packages in one place. Your dream journey starts here — fast, easy, and hassle-free.
          </Text>

          <HStack spacing={4} flexWrap="wrap" justify="center">
            <Button
              variant="solid"
              bg="white"
              color="brand.500"
              px={8}
              py={6}
              fontWeight="bold"
              borderRadius="xl"
              leftIcon={<FaTicketAlt />}
              _hover={{ bg: "whiteAlpha.900", transform: "scale(1.05)", transition: "0.3s" }}
            >
              Book a Ticket
            </Button>
            <Button
              variant="outline"
              borderColor="white"
              color="white"
              px={8}
              py={6}
              fontWeight="bold"
              borderRadius="xl"
              _hover={{ bg: "whiteAlpha.200", transform: "scale(1.05)", transition: "0.3s" }}
            >
              Learn More
            </Button>
          </HStack>
        </VStack>
      </Container>
    </Box>
  );
}
