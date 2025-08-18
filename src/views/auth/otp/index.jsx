import React, { useRef, useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  HStack,
  Input,
  Text,
  useColorModeValue,
  useToast,
} from "@chakra-ui/react";
import DefaultAuth from "layouts/auth/Default";
import illustration from "assets/img/layout/banner.png";
import { verifyOtp, sendOtp } from "services/api";

function OtpVerification() {
  const textColor = useColorModeValue("navy.700", "white");
  const textColorSecondary = "gray.400";
  const textColorBrand = useColorModeValue("brand.500", "white");
  const [otp, setOtp] = useState(new Array(6).fill(""));
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const inputsRef = useRef([]);
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const phoneNumber = location.state?.phoneNumber;

  useEffect(() => {
    if (!phoneNumber) {
      navigate("/auth/signup");
    }
  }, [phoneNumber, navigate]);

  const handleChange = (value, index) => {
    if (/^\d*$/.test(value)) {
      const newOtp = [...otp];
      newOtp[index] = value;
      setOtp(newOtp);
      if (value && index < 5) {
        inputsRef.current[index + 1].focus();
      }
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputsRef.current[index - 1].focus();
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const code = otp.join("");
      await verifyOtp(phoneNumber, code);
      toast({
        title: "Verification Successful",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      navigate("/dashboard");
    } catch (err) {
      setError(err);
      toast({
        title: "Verification Failed",
        description: err,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await sendOtp(phoneNumber);
      toast({
        title: "OTP Resent",
        description: "A new verification code has been sent",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      setOtp(new Array(6).fill(""));
    } catch (err) {
      setError(err);
      toast({
        title: "Resend Failed",
        description: err,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DefaultAuth illustrationBackground={illustration} image={illustration}>
      <Flex
        maxW={{ base: "100%", md: "max-content" }}
        w="100%"
        mx={{ base: "auto", lg: "0px" }}
        me="auto"
        h="100%"
        alignItems="start"
        justifyContent="center"
        mb={{ base: "30px", md: "60px" }}
        px={{ base: "25px", md: "0px" }}
        mt={{ base: "40px", md: "14vh" }}
        flexDirection="column"
      >
        <Box me="auto">
          <Heading color={textColor} fontSize="36px" mb="10px">
            Verify your account
          </Heading>
          <Text mb="36px" ms="4px" color={textColorSecondary} fontSize="md">
            We’ve sent a 6-digit verification code to {phoneNumber}.
          </Text>
        </Box>
        <Flex
          zIndex="2"
          direction="column"
          w={{ base: "100%", md: "420px" }}
          maxW="100%"
          background="transparent"
          borderRadius="15px"
          mx={{ base: "auto", lg: "unset" }}
          me="auto"
          mb={{ base: "20px", md: "auto" }}
        >
          <FormControl>
            <FormLabel textAlign="center" mb="4" color={textColor}>
              Enter the code
            </FormLabel>
            <HStack justify="center" mb="6" spacing="4">
              {otp.map((digit, index) => (
                <Input
                  key={index}
                  ref={(el) => (inputsRef.current[index] = el)}
                  value={digit}
                  onChange={(e) => handleChange(e.target.value, index)}
                  onKeyDown={(e) => handleKeyDown(e, index)}
                  maxLength={1}
                  textAlign="center"
                  fontSize="2xl"
                  fontWeight="bold"
                  w="60px"
                  h="60px"
                  variant="auth"
                  isDisabled={isLoading}
                />
              ))}
            </HStack>
            {error && (
              <Text color="red.500" textAlign="center" mb="4">
                {error}
              </Text>
            )}
            <Button
              fontSize="sm"
              variant="brand"
              fontWeight="500"
              w="100%"
              h="50px"
              mb="4"
              onClick={handleSubmit}
              isDisabled={otp.includes("") || isLoading}
              isLoading={isLoading}
            >
              Confirm
            </Button>
            <Text textAlign="center" color={textColorSecondary} fontSize="sm">
              Didn’t receive the code?{" "}
              <Text
                as="span"
                color={textColorBrand}
                fontWeight="500"
                cursor="pointer"
                onClick={handleResend}
              >
                Resend
              </Text>
            </Text>
          </FormControl>
        </Flex>
      </Flex>
    </DefaultAuth>
  );
}

export default OtpVerification;