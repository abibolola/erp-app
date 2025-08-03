import axios from "../../../shared/utils/api";

export const login = async (email, password) => {
  const response = await axios.post("/auth/login", { email, password });
  return response.data; // { access_token, token_type }
};
