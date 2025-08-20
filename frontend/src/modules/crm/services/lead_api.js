import axios from "../../../shared/utils/api";

export const fetchLeads = async () => {
  const response = await axios.get("/leads");
  return response.data; // [{ id, name, email, ... }]
};
