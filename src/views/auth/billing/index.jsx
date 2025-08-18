import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  InputGroup,
  InputRightElement,
  Select,
  Text,
  useColorModeValue,
  HStack,
  Divider,
} from "@chakra-ui/react";
import DefaultAuth from "layouts/auth/Default";
import illustration from "assets/img/layout/banner.png";
import { MdOutlineRemoveRedEye } from "react-icons/md";
import { RiEyeCloseLine } from "react-icons/ri";

export default function BillingPage() {
  const textColor = useColorModeValue("navy.700", "white");
  const textColorSecondary = "gray.400";
  const textColorBrand = useColorModeValue("brand.500", "white");
  const [show, setShow] = useState(false);
  const handleClick = () => setShow(!show);

  const [billingData, setBillingData] = useState({
    cardName: "",
    cardNumber: "",
    expiry: "",
    cvv: "",
    billingAddress: "",
    city: "",
    state: "",
    zip: "",
    country: "",
    paymentMethod: "credit",
  });

  const handleChange = (e) => {
    setBillingData({ ...billingData, [e.target.name]: e.target.value });
  };

  const handlePay = () => {
    alert("Payment successful!");
  };

  return (
    <DefaultAuth illustrationBackground={illustration} image={illustration}>
      <Flex
        w="100%"
        maxW={{ base: "100%", md: "420px" }}
        mx="auto"
        h="100%"
        alignItems="start"
        justifyContent="center"
        mt={{ base: "40px", md: "14vh" }}
        flexDirection="column"
        px={{ base: "25px", md: "0px" }}
      >
        <Box mb="30px">
          <Heading color={textColor} fontSize="36px" mb="10px">
            Billing & Payment
          </Heading>
          <Text mb="36px" color={textColorSecondary} fontWeight="400" fontSize="md">
            Enter your billing details and pay for your reservation
          </Text>
        </Box>

        <Flex
          direction="column"
          w="100%"
          background="transparent"
          borderRadius="15px"
          mb={{ base: "20px", md: "auto" }}
        >
          <FormControl mb="20px">
            <FormLabel color={textColor} fontWeight="500">
              Payment Method
            </FormLabel>
            <Select
              name="paymentMethod"
              value={billingData.paymentMethod}
              onChange={handleChange}
              variant="auth"
            >
              <option value="credit">Credit Card</option>
              <option value="paypal">PayPal</option>
              <option value="crypto">Crypto</option>
            </Select>
          </FormControl>

          <FormControl mb="20px">
            <FormLabel color={textColor} fontWeight="500">
              Cardholder Name
            </FormLabel>
            <Input
              name="cardName"
              value={billingData.cardName}
              onChange={handleChange}
              placeholder="Cardholder Name"
              variant="auth"
            />
          </FormControl>

          <FormControl mb="20px">
            <FormLabel color={textColor} fontWeight="500">
              Card Number
            </FormLabel>
            <Input
              name="cardNumber"
              value={billingData.cardNumber}
              onChange={handleChange}
              placeholder="Card Number"
              variant="auth"
            />
          </FormControl>

          <HStack spacing={4} mb="20px">
            <FormControl>
              <FormLabel color={textColor} fontWeight="500">
                Expiry
              </FormLabel>
              <Input
                name="expiry"
                value={billingData.expiry}
                onChange={handleChange}
                placeholder="MM/YY"
                variant="auth"
              />
            </FormControl>

            <FormControl>
              <FormLabel color={textColor} fontWeight="500">
                CVV
              </FormLabel>
              <InputGroup>
                <Input
                  name="cvv"
                  value={billingData.cvv}
                  onChange={handleChange}
                  placeholder="CVV"
                  type={show ? "text" : "password"}
                  variant="auth"
                />
                <InputRightElement mt="4px">
                  <MdOutlineRemoveRedEye
                    style={{ cursor: "pointer" }}
                    onClick={handleClick}
                  />
                </InputRightElement>
              </InputGroup>
            </FormControl>
          </HStack>

          <Divider mb="20px" />

          <FormControl mb="20px">
            <FormLabel color={textColor} fontWeight="500">
              Billing Address
            </FormLabel>
            <Input
              name="billingAddress"
              value={billingData.billingAddress}
              onChange={handleChange}
              placeholder="Street Address"
              variant="auth"
            />
          </FormControl>

          <HStack spacing={4} mb="20px">
            <FormControl>
              <Input
                name="city"
                value={billingData.city}
                onChange={handleChange}
                placeholder="City"
                variant="auth"
              />
            </FormControl>
            <FormControl>
              <Input
                name="state"
                value={billingData.state}
                onChange={handleChange}
                placeholder="State"
                variant="auth"
              />
            </FormControl>
          </HStack>

          <HStack spacing={4} mb="20px">
            <FormControl>
              <Input
                name="zip"
                value={billingData.zip}
                onChange={handleChange}
                placeholder="ZIP Code"
                variant="auth"
              />
            </FormControl>
            <FormControl>
              <Input
                name="country"
                value={billingData.country}
                onChange={handleChange}
                placeholder="Country"
                variant="auth"
              />
            </FormControl>
          </HStack>

          <Button
            fontSize="sm"
            variant="brand"
            fontWeight="500"
            w="100%"
            h="50px"
            mb="24px"
            onClick={handlePay}
          >
            Pay Now
          </Button>
        </Flex>
      </Flex>
    </DefaultAuth>
  );
}
