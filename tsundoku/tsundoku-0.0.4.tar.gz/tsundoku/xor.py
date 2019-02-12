


from IPython.display import display, Markdown, Latex


xor_model = """
**Remember how to initialize the Multi-Layered Perceptron?**

Using the `nn.Sequntial`, chained with repeated `torch.nn.Linear` + `torch.nn.Sigmoid` layers.
<br>
```python
    # Step 1: Initialization.
    # Use Sequential to define a simple feed-forward network.
    model = nn.Sequential(
                # Use nn.Linear to get our simple perceptron.
                nn.Linear(input_dim, hidden_dim),
                # Use nn.Sigmoid to get our sigmoid non-linearity.
                nn.Sigmoid(),
                # Second layer neurons.
                nn.Linear(hidden_dim, output_dim),
                nn.Sigmoid()
            )
```

**Forgotten how to initialize the optimizer and loss function?**

We can use the simple Stochastic Gradient Descent from `torch.optim.SGD`.
And for the loss, the simple Mean Square Error (MSE) aka. L2 Loss with `torchn.nn.MSELoss`.
<br>
```python
# Initialize the optimizer
learning_rate = 0.3
optimizer = optim.SGD(model.parameters(), lr=learning_rate)
# Initialize the loss function.
criterion = nn.MSELoss()
```
"""

def hint_xor_model():
    display(Markdown(xor_model))
