import React from "react";
import {
  Box,
  Container,
  Flex,
  HStack,
  Link,
  Button,
  IconButton,
  Collapse,
  Stack,
  Image,
  useDisclosure,
} from "@chakra-ui/react";
import { HamburgerIcon, CloseIcon } from "@chakra-ui/icons";
import { FaRocket, FaUser} from 'react-icons/fa';
import { Link as RouterLink } from "react-router-dom";
import logoSvg from "assets/img/logos/logo-badraghe.svg";
import { useAuth } from "../../useAuth";

export default function NavbarMinimal({ logo, navLinks = ["Home", "Features", "Pricing", "Contact"] }) {
  const { isOpen, onToggle } = useDisclosure();
  const { user } = useAuth();

  return (
    <Box
      bg="white"
      borderBottom="1px solid"
      borderColor="gray.200"
      position="sticky"
      top="0"
      zIndex="20"
    >
      <Container maxW="container.xl">
        <Flex py={4} align="center" justify="space-between">
          <Image h="36px" src={logoSvg} alt="Logo" />

          <HStack spacing={8} display={{ base: "none", md: "flex" }}>
            {navLinks.map((link) => (
              <Link key={link} fontWeight="medium" color="gray.700">
                {link}
              </Link>
            ))}
          </HStack>

          <HStack spacing={4} display={{ base: "none", md: "flex" }}>
  {user ? (
    <Button
      as={RouterLink}
      to="/user/profile"
      colorScheme="blue"
      variant="solid"
      rounded="full"
    >
      {user.name || "Profile"}
    </Button>
  ) : (
    <>
      <Button
        variant="outline"
        as={RouterLink}
        to="/auth/sign-in"
        color="gray.700"
        rounded="full"
        leftIcon={<FaUser />}
      >
        Log In
      </Button>
      <Button
        as={RouterLink}
        to="/auth/sign-up"
        colorScheme="blue"
        variant="solid"
        rounded="full"
        leftIcon={<FaRocket />}
      >
        Sign Up
      </Button>
    </>
  )}
</HStack>



          <IconButton
            display={{ base: "flex", md: "none" }}
            onClick={onToggle}
            icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
            variant="ghost"
            aria-label="Toggle Navigation"
          />
        </Flex>

        <Collapse in={isOpen} animateOpacity>
          <Stack py={4} display={{ md: "none" }} spacing={4}>
            {navLinks.map((link) => (
              <Link key={link} fontWeight="medium" color="gray.700">
                {link}
              </Link>
            ))}
            <Button variant="outline" color="gray.700">
              Log In
            </Button>
            <Button colorScheme="blue" variant="solid">
              Sign Up
            </Button>
          </Stack>
        </Collapse>
      </Container>
    </Box>
  );
}
