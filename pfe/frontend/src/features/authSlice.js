import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import authService from "./authService";

const user = JSON.parse(localStorage.getItem("user"))



// Define async thunk for creating a project
export const createProject = createAsyncThunk(
    "auth/createProject",
    async (projectData, thunkAPI) => {
      try {
        // Get the access token from the state
        const accessToken = thunkAPI.getState().auth.user.access;
        // Call the authService.createProject function passing the project data and access token
        return await authService.createProject(projectData, accessToken);
      } catch (error) {
        // Handle any errors
        return thunkAPI.rejectWithValue(error.message);
      }
    }
  );
  
  // Define async thunk for fetching user's projects
  export const fetchProjects = createAsyncThunk(
    "auth/fetchProjects",
    async (userData, thunkAPI) => {
      try {
        // Get the access token from the state
        const accessToken = thunkAPI.getState().auth.user.access;
        // Call the authService.fetchProjects function passing the access token
        return await authService.fetchProjects(userData,accessToken);
      } catch (error) {
        // Handle any errors
        return thunkAPI.rejectWithValue(error.message);
      }
    }
  );


const initialState = {
    user: user ? user : null,
    userInfo: {},
    isError: false,
    isSuccess: false,
    isLoading: false,
    message: "",
}

export const createUser = createAsyncThunk(
    "auth/register",
    async (userData, thunkAPI) => {
        try {
            return await authService.register(userData)
        } catch (error) {
            const message = (error.response && error.response.data
                && error.response.data.message) ||
                error.message || error.toString()

            return thunkAPI.rejectWithValue(message)
        }
    }
)

export const login = createAsyncThunk(
    "auth/login",
    async (userData, thunkAPI) => {
        try {
            return await authService.login(userData)
        } catch (error) {
            const message = (error.response && error.response.data
                && error.response.data.message) ||
                error.message || error.toString()

            return thunkAPI.rejectWithValue(message)
        }
    }
)

export const logout = createAsyncThunk(
    "auth/logout",
    async () => {
        authService.logout()
    }
)

export const activate = createAsyncThunk(
    "auth/activate",
    async (userData, thunkAPI) => {
        try {
            return await authService.activate(userData)
        } catch (error) {
            const message = (error.response && error.response.data
                && error.response.data.message) ||
                error.message || error.toString()

            return thunkAPI.rejectWithValue(message)
        }
    }
)

export const resetPassword = createAsyncThunk(
    "auth/resetPassword",
    async (userData, thunkAPI) => {
        try {
            return await authService.resetPassword(userData)
        } catch (error) {
            const message = (error.response && error.response.data
                && error.response.data.message) ||
                error.message || error.toString()

            return thunkAPI.rejectWithValue(message)
        }
    }
)

export const resetPasswordConfirm = createAsyncThunk(
    "auth/resetPasswordConfirm",
    async (userData, thunkAPI) => {
        try {
            return await authService.resetPasswordConfirm(userData)
        } catch (error) {
            const message = (error.response && error.response.data
                && error.response.data.message) ||
                error.message || error.toString()

            return thunkAPI.rejectWithValue(message)
        }
    }
)

export const getUserInfo = createAsyncThunk(
    "auth/getUserInfo",
    async (_, thunkAPI) => {
        try {
            const accessToken = thunkAPI.getState().auth.user.access
            return await authService.getUserInfo(accessToken)
        } catch (error) {
            const message = (error.response && error.response.data
                && error.response.data.message) ||
                error.message || error.toString()

            return thunkAPI.rejectWithValue(message)
        }
   }
)



export const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        reset: (state) => {
            state.isLoading = false
            state.isError = false
            state.isSuccess = false
            state.message = false
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(createUser.pending, (state) => {
                state.isLoading = true
            })
            .addCase(createUser.fulfilled, (state, action) => {
                state.isLoading = false
                state.isSuccess = true
                state.user = action.payload
            })
            .addCase(createUser.rejected, (state, action) => {
                state.isLoading = false
                state.isSuccess = false
                state.isError = true
                state.message = action.payload
                state.user = null
            })
            .addCase(login.pending, (state) => {
                state.isLoading = true
            })
            .addCase(login.fulfilled, (state, action) => {
                state.isLoading = false
                state.isSuccess = true
                state.user = action.payload
            })
            .addCase(login.rejected, (state, action) => {
                state.isLoading = false
                state.isSuccess = false
                state.isError = true
                state.message = action.payload
                state.user = null
            })
            .addCase(logout.fulfilled, (state) => {
                state.user = null
            })
            .addCase(activate.pending, (state) => {
                state.isLoading = true
            })
            .addCase(activate.fulfilled, (state, action) => {
                state.isLoading = false
                state.isSuccess = true
                state.user = action.payload
            })
            .addCase(activate.rejected, (state, action) => {
                state.isLoading = false
                state.isSuccess = false
                state.isError = true
                state.message = action.payload
                state.user = null
            })
            .addCase(resetPassword.pending, (state) => {
                state.isLoading = true
            })
            .addCase(resetPassword.fulfilled, (state) => {
                state.isLoading = false
                state.isSuccess = true
            })
            .addCase(resetPassword.rejected, (state, action) => {
                state.isLoading = false
                state.isSuccess = false
                state.isError = true
                state.message = action.payload
                state.user = null
            })
            .addCase(resetPasswordConfirm.pending, (state) => {
                state.isLoading = true
            })
            .addCase(resetPasswordConfirm.fulfilled, (state) => {
                state.isLoading = false
                state.isSuccess = true
            })
            .addCase(resetPasswordConfirm.rejected, (state, action) => {
                state.isLoading = false
                state.isSuccess = false
                state.isError = true
                state.message = action.payload
                state.user = null
            })
            .addCase(getUserInfo.fulfilled, (state, action) => {
                state.userInfo = action.payload
            })
            // Handle createProject.pending action
    builder.addCase(createProject.pending, (state) => {
        state.isLoading = true;
      });
      // Handle createProject.fulfilled action
      builder.addCase(createProject.fulfilled, (state, action) => {
        // Update state with the newly created project
        // Here you can update the state.projects array with the new project data if needed
        state.isLoading = false;
      });
      // Handle createProject.rejected action
      builder.addCase(createProject.rejected, (state, action) => {
        // Handle any errors
        state.isLoading = false;
        state.isError = true;
        state.message = action.payload;
      });
  
      // Handle fetchProjects.pending action
      builder.addCase(fetchProjects.pending, (state) => {
        state.isLoading = true;
      });
      // Handle fetchProjects.fulfilled action
      builder.addCase(fetchProjects.fulfilled, (state, action) => {
        // Update state with the fetched projects
        // Here you can update the state.projects array with the fetched projects data
        state.isLoading = false;
      });
      // Handle fetchProjects.rejected action
      builder.addCase(fetchProjects.rejected, (state, action) => {
        // Handle any errors
        state.isLoading = false;
        state.isError = true;
        state.message = action.payload;
      });
    }
})




export const { reset } = authSlice.actions

export default authSlice.reducer