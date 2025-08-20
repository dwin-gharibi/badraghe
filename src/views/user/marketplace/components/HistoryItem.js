import React from "react";
import { Flex, Icon, Image, Text, useColorModeValue } from "@chakra-ui/react";
import Card from "components/card/Card.js";
import { FaPlane, FaTrain, FaBus } from "react-icons/fa";

export default function NFT(props) {
  const { transportType, name, author, date, price } = props;
  const textColor = useColorModeValue("brands.900", "white");
  const bgItem = useColorModeValue(
    { bg: "white", boxShadow: "0px 40px 58px -20px rgba(112, 144, 176, 0.12)" },
    { bg: "navy.700", boxShadow: "unset" }
  );
  const textColorDate = useColorModeValue("secondaryGray.600", "white");

  const transportIcons = {
    plane: FaPlane,
    train: FaTrain,
    bus: FaBus,
  };

  const TransportIcon = transportIcons[transportType] || FaPlane;

  return (
    <Card
      _hover={bgItem}
      bg="transparent"
      boxShadow="unset"
      px="24px"
      py="21px"
      transition="0.2s linear"
    >
      <Flex direction={{ base: "column" }} justify="center">
        <Flex position="relative" align="center">
          <Flex
            align="center"
            justify="center"
            w="66px"
            h="66px"
            borderRadius="20px"
            me="16px"
            boxShadow="sm"
          >
            <Icon as={TransportIcon} w="28px" h="28px" color="brand.500" />
          </Flex>

          <Flex
            direction="column"
            w={{ base: "70%", md: "100%" }}
            me={{ base: "4px", md: "32px", xl: "10px", "3xl": "32px" }}
          >
            <Text
              color={textColor}
              fontSize="md"
              mb="5px"
              fontWeight="bold"
              me="14px"
            >
              {name}
            </Text>
            <Text color="secondaryGray.600" fontSize="sm" fontWeight="400" me="14px">
              {author}
            </Text>
          </Flex>
          <Text ms="auto" fontWeight="700" fontSize="sm" color={textColorDate}>
            {date}
          </Text>
        </Flex>
      </Flex>
    </Card>
  );
}
