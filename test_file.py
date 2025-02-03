lines = []
for i in range(1, 151):
    lines.append(f"print('This is test line number {i}: Lorem ipsum dolor sit amet, consectetur adipiscing elit.')\n")

with open(__file__, 'a') as f:
    f.write(''.join(lines))

# End of test file. 