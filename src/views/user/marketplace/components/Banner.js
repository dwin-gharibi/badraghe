import React from "react";
import { Button, Flex, Link, Text } from "@chakra-ui/react";

import banner from "assets/img/auth/dashboard-banner.png";

export default function Banner() {
  return (
    <Flex
      direction='column'
      bgSize='cover'
      bgImage={banner}
      py={{ base: "30px", md: "56px" }}
      px={{ base: "30px", md: "64px" }}
      borderRadius='30px'>
      <Text
        fontSize={{ base: "24px", md: "34px" }}
        color='white'
        mb='14px'
        maxW={{
          base: "100%",
          md: "64%",
          lg: "46%",
          xl: "70%",
          "2xl": "50%",
          "3xl": "42%",
        }}
        fontWeight='700'
        lineHeight={{ base: "32px", md: "42px" }}>
        Discover seamless travel with Badraghe
      </Text>
      <Text
        fontSize='md'
        color='#E3DAFF'
        maxW={{
          base: "100%",
          md: "64%",
          lg: "40%",
          xl: "56%",
          "2xl": "46%",
          "3xl": "34%",
        }}
        fontWeight='500'
        mb='40px'
        lineHeight='28px'>
        From buses to planes, we connect you with the tickets you need at the prices you love.
        Travel made easy, reliable, and built around you.
      </Text>
      <Flex align='center'>
        <Button
          bg='white'
          color='black'
          _hover={{ bg: "whiteAlpha.900" }}
          _active={{ bg: "white" }}
          _focus={{ bg: "white" }}
          fontWeight='500'
          fontSize='14px'
          as={Link}
          to="/user/reserve"
          py='20px'
          px='27'
          me='38px'>
          Buy a ticket now
        </Button>
        <Link>
          <Text color='white' fontSize='sm' fontWeight='500'>
            Learn more
          </Text>
        </Link>
      </Flex>
    </Flex>
  );
}
